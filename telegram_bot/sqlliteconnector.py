import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('Test.session')

# Create a cursor object using the cursor() method
cursor = connection.cursor()

# For demonstration, let's execute a simple SQL query
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch and display the result
tables = cursor.fetchall()
for table in tables:
	print(table)

# Don't forget to close the connection
connection.close()
