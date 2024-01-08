import pymysql as mq

mysql = mq.connect(host='localhost',
    database='workdiary',
    user='root',
    password='')
mycursor = mysql.cursor()

print("{:<15}{:<20}{:<20}".format("Employee Name", "From Date", "To Time", "workdetails", "workstory"))

try:
    name = input("Enter the Employee id: ")
    fromdate = input("Enter the From Time: ")
    todate = input("Enter the To Time: ")
    sql = "SELECT * FROM workdetails WHERE employee_id = '" + name + "' AND from_time = '" + fromdate + "' AND to_time = '" + todate + "'"

    mycursor.execute(sql)  # Execute the SQL query
    sdata = mycursor.fetchall()

    for s in sdata:
        print("{:<15}{:<20}{:<20}".format(s[2], s[3], s[4]))

except mq.Error as e:
    print(f"Error: {e}")

finally:
    mycursor.close()
    mysql.close()
