import pymysql as mq

# Connect to the database
mysql = mq.connect(host='localhost', user='root', password='', database='workdiary')
mycursor = mysql.cursor()

# Retrieve the date range and employee name
from_date = input("Enter the From Date (YYYY-MM-DD): ")
to_date = input("Enter the To Date (YYYY-MM-DD): ")
employee_name = input("Enter the Employee Name: ")

# Retrieve work stories and employee names for the specified date range and employee
sql = "SELECT e.Employee_Name, w.work_story " \
      "FROM workdetails w " \
      "INNER JOIN employees e ON w.employee_id = e.Employee_ID " \
      "WHERE DATE(w.from_time) BETWEEN %s AND %s " \
      "AND e.Employee_Name = %s"

mycursor.execute(sql, (from_date, to_date, employee_name))
data = mycursor.fetchall()

if not data:
    print(f"No work stories found for {employee_id} from {from_date} to {to_date}")
else:
    print(f"Work stories for {employee_id} from {from_date} to {to_date}:")
    for row in data:
        print(f"Employee Name: {row[2]}, Work Story: {row[8]}")

# Close the cursor and the database connection
mycursor.close()
mysql.close()
