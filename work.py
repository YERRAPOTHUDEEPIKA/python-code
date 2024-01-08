import pymongo
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["workdetails"]
collection = db["workdetails"]

start_date = datetime(2023, 10, 4)
end_date = datetime(2023, 10, 5)

query = {
    "date": {"$gte": start_date, "$lte": end_date}
}
work_stories = collection.find(query)

all_employees = set()
for story in work_stories:
    all_employees.add(story["employee_id"])

team_leaders = set()
for employee in all_employees:
    employee_id = collection.find_one({"employee_id": employee})
    team_leader = employee_id.get("team_leader")
    if team_leader:
        team_leaders.add(team_leader)

visible_employees = all_employees - team_leaders

print("Work Stories:")
for story in work_stories:
    if story["employee_id"] in visible_employees:
        print(f"Date: {story['date']}, Employee: {story['employee_id']}, Work Story: {story['work_story']}")

print("\nVisible Employees:")
for employee in visible_employees:
    print(employee)
