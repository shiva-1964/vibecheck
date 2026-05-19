import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

# ─── Analyses Table ─────────────────────────────────────────

cursor.execute('''
CREATE TABLE IF NOT EXISTS analyses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    text TEXT,

    toxicity_score REAL,

    emotions TEXT,

    verdict TEXT,

    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

)
''')

# ─── Users Table ────────────────────────────────────────────

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT

)
''')

conn.commit()

conn.close()

print("Database and tables created successfully!")