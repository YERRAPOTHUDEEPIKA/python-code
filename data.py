from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017'  # Replace with your MongoDB URI
DB_NAME = 'Data'  # Replace with your database name
COLLECTION_NAME = 'userdata'  # Replace with your collection name

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Function to fetch values of a particular field as a Python array
def get_field_values_as_array(field_name):
    data = collection.find({}, {field_name: 1, '_id': 0})  # Include only the specified field, exclude _id
    values = [document.get(field_name) for document in data if field_name in document]
    return values

# Example usage:
if __name__ == '__main__':
    field_name = 'Customer_phone'  # Replace with the field name you want to fetch
    field_values = get_field_values_as_array(field_name)

    # Save the field values to a text file
    with open('field_values.txt', 'w') as file:
        for value in field_values:
            file.write(str(value) + '\n')