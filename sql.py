import mysql.connector

# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'workdiary',
    'user': 'root',
    'password': 'K@ppsoft123'  # Replace with your actual MySQL password
}

def get_user_details_by_name(user_name):
    try:
        # Establish a connection
        connection = mysql.connector.connect(**db_config)

        # Create a cursor
        cursor = connection.cursor()

        # Execute an SQL query to retrieve all details of a user based on their name
        query = "SELECT * FROM workdetails WHERE name = %as"
        cursor.execute(query, (user_name,))

        # Fetch data
        result = cursor.fetchone()

        if result:
            user_details = {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'email_verified_at': result[3],
                'password': result[4],
                'user_level': result[5]
            }
            return user_details
        else:
            return None  # Return None if the user is not found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Example usage:
user_name = 'Madhana'  # Replace with the actual user name you want to query
user_details = get_user_details_by_name(user_name)

if user_details:
    print("User Details:")
    for key, value in user_details.items():
        print(f"{key}: {value}")
else:
    print("User not found.")
