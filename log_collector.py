import csv

def main():
    logs = [
        {"timestamp": "2025-06-17 12:00:00", "event": "User login", "status": "success"},
        {"timestamp": "2025-06-17 12:05:00", "event": "File upload", "status": "failed"}
    ]

    with open("logs.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "event", "status"])
        writer.writeheader()
        writer.writerows(logs)

    print("✅ logs.csv created successfully!")

if __name__ == "__main__":
    main()
