import pymysql as mq
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Connect to the database
mysql = mq.connect(host='localhost', user='root', password='K@ppsoft123', database='workdiary')
mycursor = mysql.cursor()

# Retrieve data from your SQL table
sql = "SELECT DATE(from_time) AS date, work_story FROM workdetails"
mycursor.execute(sql)
data = mycursor.fetchall()

# Create a DataFrame from the SQL data
df = pd.DataFrame(data, columns=['Date', 'work_story'])

# Convert the 'Date' column to a datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Group the data by date and count the number of work stories for each date
daily_counts = df.groupby('Date').count()

# # Create a calendar plot
fig, ax = plt.subplots(figsize=(12, 6))

daily_counts.plot(kind='bar', ax=ax)

ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
ax.set_ylabel('work_story')
ax.set_xlabel('Date')
ax.set_title('work_story Calendar')

plt.tight_layout()
plt.show()

# Close the cursor and the database connection
mycursor.close()
mysql.close()
