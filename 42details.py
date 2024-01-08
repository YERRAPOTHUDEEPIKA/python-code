import mysql.connector

# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'workdiary',
    'user': 'root',
    'password': 'K@ppsoft123'
}

def get_workdetails_by_name(user_name):
    try:
        # Establish a connection
        connection = mysql.connector.connect(**db_config)

        # Create a cursor
        cursor = connection.cursor()

        # Execute an SQL query to retrieve work details for a specific user based on their name
        query = "SELECT * FROM workdetails WHERE employee_id = %s"
        cursor.execute(query, (user_name,))

        # Fetch data
        result = cursor.fetchall()

        for row in result:
            print(row)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Example usage:
user_name = '42'  # Replace with the actual user name you want to query
get_workdetails_by_name(user_name)
