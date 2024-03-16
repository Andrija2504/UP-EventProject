import psycopg2
import pandas as pd

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
cur.execute("Delete from event")
# Insert data
df = pd.read_csv("CsvFiles/Combined.csv")

for index, row in df.iterrows():
    query = """
    INSERT INTO event (name, description, link, date, location) 
    VALUES (%s, %s, %s, %s, %s);
    """

    title = row['Title'] if pd.notna(row['Title']) else ''
    title = title.strip()
    description = row['Description'] if pd.notna(row['Description']) else ''
    description = description.strip()
    links = row['Link'] if pd.notna(row['Link']) else ''
    links = links.strip()
    date = row['Date'] if pd.notna(row['Date']) else ''
    date = date.strip()
    location = row['Location'] if pd.notna(row['Location']) else ''
    location = location.strip()

    try:
        cur.execute(query, (title, description, links, date, location))
    except psycopg2.Error as e:
        print(f"Error inserting row {index}: {e}")
        conn.rollback()
    else:
        conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()