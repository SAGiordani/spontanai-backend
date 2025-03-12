import os
import csv
from datetime import datetime

LOG_FILE = "logs/test_activity_logs.csv"

# Ensure the logs folder exists
os.makedirs("logs", exist_ok=True)

def log_to_csv():
    log_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not log_exists:
                writer.writerow(["Timestamp", "Test Data"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "This is a test log"])
        print("✅ Log saved successfully!")
    except Exception as e:
        print(f"❌ Error writing to log file: {e}")

log_to_csv()
