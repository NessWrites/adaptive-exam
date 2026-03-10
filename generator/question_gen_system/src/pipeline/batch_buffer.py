from collections import deque

BATCH_SIZE = 2

question_buffer = deque()

def add_to_buffer(rows):

    question_buffer.extend(rows)

    if len(question_buffer) >= BATCH_SIZE:

        batch = [question_buffer.popleft() for _ in range(BATCH_SIZE)]

        return batch
    
    return None


def current_buffer_size():
    return len(question_buffer)