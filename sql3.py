from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'workdiary',
    'user': 'root',
    'password': ''
}

@app.route('/', methods=['GET', 'POST'])
def display_filtered_data():
    try:
        # Establish a connection
        connection = mysql.connector.connect(**db_config)

        # Create a cursor
        cursor = connection.cursor()

        # Define filters based on user input from the HTML form
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        employee_id = request.form.get('employee_id')
        work_story = request.form.get('work_story')

        # Build and execute a SQL query with the specified filters
        query = "SELECT * FROM your_table WHERE date BETWEEN %s AND %s"
        params = (start_date, end_date)
        
        if employee_id:
            query += " AND employee_id = %s"
            params += (employee_id,)

        if work_story:
            query += " AND work_story LIKE %s"
            params += (f"%{work_story}%",)

        cursor.execute(query, params)

        # Fetch data
        result = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        result = []

    finally:
        if 'connection' in locals() and connection.is_connected():
            # Close the cursor and connection
            cursor.close()
            connection.close()

    return render_template('filtereddata.html', data=result)

if __name__ == '__main__':
    app.run(debug=True)
