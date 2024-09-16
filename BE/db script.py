import sqlite3
import os

# Define the path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'skills.db')

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect(DB_PATH)

# Create a cursor object
cursor = conn.cursor()

# Create the `skills` table
cursor.execute('''
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,
    icon TEXT NOT NULL
)
''')

# Create the `about` table
cursor.execute('''
CREATE TABLE IF NOT EXISTS about (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT
)
''')

# Insert a default record into the `about` table (if it doesn't exist)
cursor.execute('''
INSERT OR IGNORE INTO about (id, title, description) VALUES (1, '', '')
''')

# Create the `cv` table
cursor.execute('''
CREATE TABLE IF NOT EXISTS cv (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    upload_date TEXT
)
''')

# Create the `social_links` table
cursor.execute('''
CREATE TABLE IF NOT EXISTS social_links (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database setup completed. Database file created at: {DB_PATH}")
