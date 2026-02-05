# locustfile.py
import random
from locust import HttpUser, task, between

class ExamUser(HttpUser):
    wait_time = between(1, 3) # Simulates user thinking time (1-3 seconds)
    
    def on_start(self):
        """Executed when a user spawns"""
        self.session_id = None
        self.current_q_id = None
        self.options = []

    @task(1)
    def take_exam(self):
        # 1. Start Exam
        with self.client.get("/exam/start", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                self.current_q_id = data['question']['unique_id']
                self.options = data['question']['options']
            else:
                response.failure(f"Failed to start: {response.status_code}")
                return

        # 2. Loop through questions (Simulate 50 questions)
        for i in range(50):
            if not self.session_id:
                break
                
            # Pick a random answer (A, B, C, or D)
            # Assuming options are ["Option A", "Option B"...] or just texts
            # We pick a random letter to be safe
            answer = random.choice(["A", "B", "C", "D"])
            
            payload = {
                "session_id": self.session_id,
                "user_answer": answer
            }
            
            with self.client.post("/exam/submit-answer", json=payload, catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['exam_completed']:
                        # Exam done, break loop
                        break
                    
                    if data.get('next_question'):
                        self.current_q_id = data['next_question']['unique_id']
                        self.options = data['next_question']['options']
                else:
                    response.failure(f"Submit failed: {response.text}")
                    break
        
        # 3. Get Results
        if self.session_id:
            self.client.get(f"/exam/results/{self.session_id}")