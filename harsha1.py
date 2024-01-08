from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configure MySQL connection
db = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password=" ",
    database="workdiary"
)
cursor = db.cursor()

@app.route('/')
def index():
    # Retrieve the list of employees
    cursor.execute("SELECT DISTINCT employee_id FROM workdetails")
    employees = [row[0] for row in cursor.fetchall()]

    return render_template('workdiary1.html', employees=employees)

@app.route('/workdetails', methods=['GET'])
def workdetails():
    # Get the selected employee, from_date, and to_date
    employee_id = request.args.get('employee_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    # Retrieve work details based on the selected employee and date range
    cursor.execute("SELECT * FROM workdetails WHERE employee_id = %s AND date BETWEEN %s AND %s", (employee_id, from_date, to_date))
    work_details = cursor.fetchall()

    return render_template('workdiary1.html', employees=[], work_details=work_details)

if __name__ == '__main__':
    app.run(debug=True)


