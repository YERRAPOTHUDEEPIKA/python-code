import mysql.connector

# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'workdiary',
    'user': 'root',
    'password': 'K@ppsoft123'  # Replace with your actual MySQL password
}

def get_username_by_id(user_id):
    try:
        # Establish a connection
        connection = mysql.connector.connect(**db_config)

        # Create a cursor
        cursor = connection.cursor()

        # Execute an SQL query to retrieve the user's name based on their ID
        query = "SELECT name FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))

        # Fetch data
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the first column (name)
        else:
            return None  # Return None if no matching user is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Example usage:
user_id = 42  # Replace with the actual user ID you want to query
user_name = get_username_by_id(user_id)

if user_name:
    print(f"User Name: {user_name}")
else:
    print("User not found.")
