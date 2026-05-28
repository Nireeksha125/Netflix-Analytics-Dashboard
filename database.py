import pandas as pd
import sqlite3

# Read Dataset
df = pd.read_csv(
    "dataset/mymoviedb.csv",
    engine='python',
    on_bad_lines='skip'
)

# Create Database
conn = sqlite3.connect("netflix.db")

cursor = conn.cursor()

# Store Movie Dataset
df.to_sql(
    "movies",
    conn,
    if_exists="replace",
    index=False
)

# Create Search History Table
cursor.execute("""

CREATE TABLE IF NOT EXISTS search_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    movie_name TEXT

)

""")

conn.commit()

print("Database Created Successfully!")

conn.close()