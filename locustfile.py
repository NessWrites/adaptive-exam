import random
from locust import HttpUser, task, between, events
import logging

logger = logging.getLogger(__name__)

class ExamTaker(HttpUser):
    # Simulate a student thinking for 1-2 seconds per question
    wait_time = between(1, 2)
    
    def on_start(self):
        """Called when a user is spawned: Starts the exam session"""
        self.session_id = None
        self.exam_completed = False
        self._start_exam()

    def _start_exam(self):
        with self.client.get("/exam/start", name="01_Start_Exam") as response:
            if response.status_code == 200:
                self.session_id = response.json().get("session_id")
            else:
                response.failure(f"Could not start exam: {response.text}")

    @task
    def answer_question(self):
        """The main loop: submits an answer and handles the next question"""
        if self.exam_completed or not self.session_id:
            return

        # Simulate different types of answers (JSON Strings and JSON Lists)
        # This tests your new JSON column property!
        if random.random() < 0.1:
            # 10% chance of a Multiple Selection (List)
            user_choice = random.sample(["A", "B", "C", "D"], 2) 
        else:
            # 90% chance of a Single Selection (String)
            user_choice = random.choice(["A", "B", "C", "D"])

        payload = {
            "session_id": self.session_id,
            "user_answer": user_choice
        }

        with self.client.post("/exam/submit-answer", json=payload, name="02_Submit_Answer") as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("exam_completed"):
                    self.exam_completed = True
                    self._get_results()
            else:
                response.failure(f"Submit failed: {response.text}")

    def _get_results(self):
        self.client.get(f"/exam/results/{self.session_id}", name="03_Get_Results")
        # After getting results, the user has finished their job. 
        # We 'stop' this user so a new one can take their place if needed.
        self.interrupt()