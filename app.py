from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017'  # Replace with your MongoDB URI
DB_NAME = 'data'  # Replace with your database name
COLLECTION_NAME = 'user'  # Replace with your collection name

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# API endpoint to fetch and return values of a particular field
@app.route('/api/field/<string:field_name>', methods=['GET'])
def get_field_values(field_name):
    data = collection.find({}, {field_name: 1, '_id': 0})  # Include only the specified field, exclude _id
    values = [document.get(field_name) for document in data if field_name in document]
    if len(values) > 0:
        return jsonify({field_name: values})
    else:
        return jsonify({"message": "Field not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
