import pymysql as mq

mysql = mq.connect(host='localhost',
    
    database= 'workdiary',
    user= 'root',
    password='')
mycursor = mysql.cursor()

print("{:<15}{:<20}{:<20}".format("Employee Name", "From Date", "To Time","workdetails"))

try:
	name=input("Enter the Employee Name:- ")
    sql = "SELECT * FROM workdetails where Employee_Name='" + name + "'"
    mycursor.execute(sql)
    sdata = mycursor.fetchall()

    for s in sdata:
        print("{:<15}{:<20}{:<20}".format(s[2], s[3], s[4]))

except mq.Error as e:
    print(f"Error: {e}")

finally:
    mycursor.close()
    mysql.close()
