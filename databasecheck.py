import psycopg2
import pandas as pd
import re
from datetime import datetime

def insert_event(name, position, email):
    query = """
    INSERT INTO event (name, position, email) 
    VALUES (%s, %s, %s);
    """
    cur.execute(query, (name, position, email))
    conn.commit()

# Connect to your database
conn = psycopg2.connect(
    dbname='test', 
    user='postgres', 
    password='', 
    host='localhost',
    client_encoding='UTF8'
)

# Open a cursor to perform database operations
cur = conn.cursor()
cur.execute("SET client_encoding TO 'UTF8'")
# Execute the query
cur.execute("SELECT * FROM event WHERE location LIKE '%izola%'")

# Regular expression to find dates in the format dd. mm. yyyy
date_pattern = r"\d{2}\. \d{2}\. \d{4}"
# Fetch the results
events = cur.fetchall()
for event in events:
    splitted = event[5].split('\n')
    matches = re.findall(date_pattern, splitted[0])
    if(len(matches) == 2):
        print(f"Event {event[1]} will be held from {matches[0]} until {matches[1]}.")
    else:
        print(f"Event {event[1]} will be held on {matches[0]}.")
# Close the cursor and the connection
cur.close()
conn.close()