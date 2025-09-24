<<<<<<< HEAD
import sqlite3

conn = sqlite3.connect('users.db')  # your database file
c = conn.cursor()

# Drop the table if it exists (safe if you have no important data)
c.execute("DROP TABLE IF EXISTS users;")

# Create users table with correct columns
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Database initialized successfully!")
=======
import sqlite3

conn = sqlite3.connect('users.db')  # your database file
c = conn.cursor()

# Drop the table if it exists (safe if you have no important data)
c.execute("DROP TABLE IF EXISTS users;")

# Create users table with correct columns
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Database initialized successfully!")
>>>>>>> 866814961c062d2ffa52ba62ffa5f29751ab00a9
