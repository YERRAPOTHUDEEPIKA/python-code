import mysql.connector

# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'workdiary',
    'user': 'root',
    'password':'K@ppsoft123'
    
}

try:
    # Establish a connection
    connection = mysql.connector.connect(**db_config)

    # Create a cursor
    cursor = connection.cursor()

    # Execute an SQL query
    query = "SELECT * FROM workdetails "
    cursor.execute(query)

    # Fetch data
    result = cursor.fetchall()
    for row in result:
        print(row)

except mysql.connector.Error as err:
    print(f"Error: {err}")
    
finally:
    if 'connection' in locals() and connection.is_connected():
        # Commit and close the cursor and connection
        connection.commit()
        cursor.close()
        connection.close()
