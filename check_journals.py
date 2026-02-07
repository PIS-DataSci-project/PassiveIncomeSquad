import sqlite3

conn = sqlite3.connect('./relational.db')
cursor = conn.cursor()

# Check if journals table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journals'")
if cursor.fetchone():
    cursor.execute("PRAGMA table_info(journals)")
    print("Journals table schema:")
    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[2]}")
else:
    print("No journals table found")
    # List all tables again
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("\nAll tables:")
    for row in cursor.fetchall():
        print(f"  {row[0]}")

conn.close()
