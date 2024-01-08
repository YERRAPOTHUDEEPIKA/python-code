import mysql.connector


# Replace these values with your database credentials
db_config = {
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'workdiary',
    'user': 'root',
    'password': ''
}

def get_filtered_data():
    # Get the filter values from input fields
    employee_name = employee_name_entry.get()
    from_date = from_date_entry.get()
    to_date = to_date_entry.get()

    # Establish a connection
    connection = mysql.connector.connect(**db_config)

    # Create a cursor
    cursor = connection.cursor()

    # Construct the SQL query with placeholders
    query = "SELECT EmployeeName, FromDate, ToDate, WorkDetails FROM workdetails " \
            "WHERE employee_id = %s AND FromDate >= %s AND ToDate <= %s"

    # Execute the query with placeholders and provide values as a tuple
    cursor.execute(query, (employee_id, from_date, to_date))

    # Fetch data
    result = cursor.fetchall()
    display_filtered_data(result)

    # Close the cursor and connection
    cursor.close()
    connection.close()

def display_filtered_data(data):
    result_text.delete(1.0, tk.END)  # Clear the existing text
    for row in data:
        result_text.insert(tk.END, f"employee_id: {row[0]}\n")
        result_text.insert(tk.END, f"From Date: {row[1]}\n")
        result_text.insert(tk.END, f"To Date: {row[2]}\n")
        result_text.insert(tk.END, f"Work Details: {row[3]}\n\n")

# Create the main window
root = tk.Tk()
root.title("Filter Data")

# Create and place input fields
tk.Label(root, text="Employee Name:").pack()
employee_name_entry = tk.Entry(root)
employee_name_entry.pack()

tk.Label(root, text="From Date:").pack()
from_date_entry = tk.Entry(root)
from_date_entry.pack()

tk.Label(root, text="To Date:").pack()
to_date_entry = tk.Entry(root)
to_date_entry.pack()

# Create and place the filter button
filter_button = tk.Button(root, text="Filter", command=get_filtered_data)
filter_button.pack()

# Create a text widget for displaying the filtered data
result_text = tk.Text(root, height=10, width=40)
result_text.pack()

root.mainloop()
