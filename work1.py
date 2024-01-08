from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['workdiary']  # Replace with your database name

@app.route('/')
def index():
    return render_template('workdiary.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    employee_name = request.form['employee_name']

    # Query MongoDB for data based on the provided criteria
    collection = db['workdetails']
    query = {
        'date': {
            '$gte': from_date,
            '$lte': to_date
        },
        'employee_name': employee_id
    }

    results = collection.find(query)

    # Convert the MongoDB cursor to a list of dictionaries
    data = [result for result in results]

    return jsonify({'data': data})

if __name__ == '__main__':
    app.run()
