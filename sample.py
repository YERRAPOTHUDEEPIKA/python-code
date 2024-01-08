import sqlite3

# Create a SQLite database or connect to an existing one
conn = sqlite3.connect('employee_data.db')
cursor = conn.cursor()

# Create a table to store employee data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee (
        employee_id INTEGER PRIMARY KEY,
        employee_name TEXT,
        work_date DATE,
        work_details TEXT
    )
''')

# Function to insert employee data
def insert_employee_data(employee_name, work_date, work_details):
    cursor.execute('''
        INSERT INTO employee (employee_name, work_date, work_details)
        VALUES (?, ?, ?)
    ''', (employee_name, work_date, work_details))
    conn.commit()

# Function to retrieve data for specific dates
def get_data_for_dates(start_date, end_date):
    cursor.execute('''
        SELECT * FROM employee
        WHERE work_date BETWEEN ? AND ?
    ''', (start_date, end_date))
    return cursor.fetchall()

# Function to get work details for a specific employee on specific dates
def get_employee_work_details(employee_name, start_date, end_date):
    cursor.execute('''
        SELECT * FROM employee
        WHERE employee_name = ? AND work_date BETWEEN ? AND ?
    ''', (employee_name, start_date, end_date))
    return cursor.fetchall()

# Example usage
if _name_ == '_main_':
    # Insert sample data
    insert_employee_data("Employee1", "2023-10-15", "Work details for Employee1 on 2023-10-15")
    insert_employee_data("Employee2", "2023-10-15", "Work details for Employee2 on 2023-10-15")
    insert_employee_data("Employee1", "2023-10-16", "Work details for Employee1 on 2023-10-16")

    # Retrieve data for specific dates
    start_date = "2023-10-15"
    end_date = "2023-10-16"
    data_for_dates = get_data_for_dates(start_date, end_date)
    print("Data for specific dates:")
    for row in data_for_dates:
        print(row)

    # Retrieve work details for a specific employee on specific dates
    employee_name = "Employee1"
    employee_work_details = get_employee_work_details(employee_name, start_date, end_date)
    print(f"Work details for {employee_name} on specific dates:")
    for row in employee_work_details:
        print(row)

# Close the database connection when done
conn.close()