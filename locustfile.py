# locustfile.py
import random
from locust import HttpUser, task, between, events
import logging

logger = logging.getLogger(__name__)


class ExamUser(HttpUser):
    """
    Simulates a user taking ONE complete exam.
    After exam completion, the user stops (doesn't restart).
    """
    wait_time = between(1, 3)  # Simulates thinking time between questions
    
    def on_start(self):
        """Executed when a user spawns - initialize state"""
        self.session_id = None
        self.current_q_id = None
        self.options = []
        self.exam_completed = False
        self.question_count = 0

    @task
    def take_exam(self):
        """
        Main task: Take one complete exam.
        This task runs once per user lifecycle.
        """
        
        # If exam already completed, stop this user
        if self.exam_completed:
            logger.info(f"User already completed exam (session {self.session_id}). Stopping.")
            self.environment.runner.quit()  # Stop this specific user
            return
        
        # Step 1: Start exam (only if not started yet)
        if not self.session_id:
            self._start_exam()
            if not self.session_id:
                # Failed to start, stop this user
                self.environment.runner.quit()
                return
        
        # Step 2: Answer current question
        if self.session_id and not self.exam_completed:
            self._submit_answer()
        
        # Step 3: If exam completed, get results and stop
        if self.exam_completed:
            self._get_results()
            logger.info(f"User completed exam with session {self.session_id}. Total questions: {self.question_count}")
            self.environment.runner.quit()  # Stop this user

    def _start_exam(self):
        """Start the exam and get first question"""
        with self.client.get("/exam/start", catch_response=True, name="Start Exam") as response:
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                self.current_q_id = data['question']['unique_id']
                self.options = data['question'].get('options', [])
                self.question_count = 1
                logger.debug(f"Started exam: session_id={self.session_id}, first_question={self.current_q_id}")
                response.success()
            else:
                response.failure(f"Failed to start exam: {response.status_code} - {response.text}")
                logger.error(f"Start exam failed: {response.text}")

    def _submit_answer(self):
        """Submit answer for current question and get next question"""
        
        # Choose a random answer
        # For better simulation, use 70% chance of "A" (simulates some correct answers)
        if random.random() < 0.7:
            answer = "A"
        else:
            answer = random.choice(["A", "B", "C", "D"])
        
        payload = {
            "session_id": self.session_id,
            "user_answer": answer
        }
        
        with self.client.post(
            "/exam/submit-answer", 
            json=payload, 
            catch_response=True,
            name="Submit Answer"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                
                # Check if exam completed
                if data.get('exam_completed', False):
                    self.exam_completed = True
                    logger.debug(f"Exam completed for session {self.session_id}")
                    response.success()
                    return
                
                # Get next question
                if data.get('next_question'):
                    self.current_q_id = data['next_question']['unique_id']
                    self.options = data['next_question'].get('options', [])
                    self.question_count += 1
                    logger.debug(f"Session {self.session_id}: Answered Q{self.question_count-1}, got Q{self.question_count}")
                    response.success()
                else:
                    response.failure("No next question and exam not marked complete")
                    self.exam_completed = True
            else:
                response.failure(f"Submit answer failed: {response.status_code} - {response.text}")
                logger.error(f"Submit failed for session {self.session_id}: {response.text}")
                self.exam_completed = True  # Stop on error

    def _get_results(self):
        """Fetch final exam results"""
        if not self.session_id:
            return
            
        with self.client.get(
            f"/exam/results/{self.session_id}",
            catch_response=True,
            name="Get Results"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Results for session {self.session_id}: "
                          f"{data.get('correct_answers')}/{data.get('total_questions')} correct, "
                          f"Accuracy: {data.get('accuracy')}%")
                response.success()
            else:
                response.failure(f"Get results failed: {response.status_code}")
                logger.error(f"Get results failed: {response.text}")


# ============================================================================
# ALTERNATIVE: One-time exam completion (better for testing)
# ============================================================================

class ExamUserOneShot(HttpUser):
    """
    Alternative approach: Each user takes ONE complete exam then stops forever.
    Better for testing realistic concurrent exam-taking scenarios.
    """
    wait_time = between(0.5, 2)  # Faster for load testing
    
    def on_start(self):
        """Take one complete exam when user spawns"""
        self.session_id = None
        self.exam_completed = False
        
        # Start exam
        response = self.client.get("/exam/start")
        if response.status_code != 200:
            logger.error(f"Failed to start exam: {response.text}")
            return
        
        data = response.json()
        self.session_id = data['session_id']
        logger.info(f"User started exam: session {self.session_id}")
        
        # Answer all 50 questions
        for i in range(50):
            # Random answer with 60% chance of "A" 
            answer = "A" if random.random() < 0.6 else random.choice(["A", "B", "C", "D"])
            
            payload = {
                "session_id": self.session_id,
                "user_answer": answer
            }
            
            response = self.client.post("/exam/submit-answer", json=payload, name="Submit Answer")
            
            if response.status_code != 200:
                logger.error(f"Failed to submit answer: {response.text}")
                break
            
            result = response.json()
            
            if result.get('exam_completed'):
                logger.info(f"Session {self.session_id} completed after {i+1} questions")
                break
        
        # Get results
        self.client.get(f"/exam/results/{self.session_id}", name="Get Results")
        
        # Mark as completed
        self.exam_completed = True
        logger.info(f"User finished exam {self.session_id}")
    
    @task
    def idle(self):
        """
        Do nothing after exam completion.
        This keeps the user "alive" in Locust stats but inactive.
        """
        if self.exam_completed:
            # Just wait - don't make any more requests
            self.environment.runner.quit()


# ============================================================================
# EVENT HANDLERS (Optional - for detailed metrics)
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Executed when test starts"""
    logger.info("=" * 60)
    logger.info("LOAD TEST STARTING")
    logger.info(f"Target: {environment.host}")
    logger.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Executed when test stops"""
    logger.info("=" * 60)
    logger.info("LOAD TEST COMPLETED")
    logger.info("=" * 60)


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

"""
USAGE:

1. Test with default user (takes exam step-by-step with delays):
   locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2

2. Test with one-shot user (each user completes full exam quickly):
   locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 ExamUserOneShot

3. Run headless (no web UI):
   locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m --headless

4. Advanced: Mixed scenario
   locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --tags exam


METRICS TO WATCH:
- Request success rate (should be >99%)
- Average response time (should be <500ms)
- Number of completed exams (should equal number of users)
- Database: exam_sessions count should equal number of users
- Database: responses count should be ~50 × number of users


REALISTIC TESTING SCENARIOS:

Scenario 1: Classroom (30 students starting exam at same time)
  locust --users 30 --spawn-rate 30 --run-time 10m

Scenario 2: Open exam window (students joining gradually)
  locust --users 100 --spawn-rate 5 --run-time 30m

Scenario 3: Stress test (max capacity)
  locust --users 500 --spawn-rate 50 --run-time 5m

"""