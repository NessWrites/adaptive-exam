import csv
import os
import threading


csv_file = "api_responses.csv"
fields = ['Domain', "Topic", "Context", "Level", "Response"]
csv_lock = threading.Lock()
def dump_to_csv(data: dict):
    file_exists = os.path.isfile(csv_file)

    with csv_lock:
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames = fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)