import pymongo
from datetime import datetime

# Replace these with your MongoDB connection details
mongo_uri = "mongodb://localhost:27017/workdetails"
client = pymongo.MongoClient(mongo_uri)

# Select your database and collection
db = client.get_database("workdetails")
collection = db.get_collection("workdetails")

# Define the start and end dates for filtering
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

# Query the database to retrieve employees within the date range
query = {"date_field_name": {"$gte": start_date, "$lte": end_date}}
# Replace "date_field_name" with the actual field name in your MongoDB document that contains the date.

# You can add more conditions to your query if needed
# query["other_field_name"] = "some_value"

# Execute the query
results = collection.find(query)

# Iterate through the results and print or process the employee data
for employee in results:
    print(employee)

# Close the MongoDB connection
client.close()
