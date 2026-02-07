import sqlite3

conn = sqlite3.connect('./relational.db')
cursor = conn.cursor()

# Check schema
cursor.execute("PRAGMA table_info(categories)")
print("Categories table schema:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

# Check sample data
print("\nSample data (first 5 rows):")
cursor.execute("SELECT * FROM categories LIMIT 5")
for row in cursor.fetchall():
    print(f"  {row}")

# Check total count
cursor.execute("SELECT COUNT(*) FROM categories")
print(f"\nTotal rows: {cursor.fetchone()[0]}")

conn.close()
