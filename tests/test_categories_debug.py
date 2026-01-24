import json
import sqlite3
import pandas as pd

# Test with an identifier that should have categories
test_id = "1471-0072"  # The ID being tested in Claudia.py

print(f"Testing with identifier: {test_id}")
print("=" * 60)

# 1. Check if it's in the JSON
print("\n1. Checking Scimago JSON:")
with open('data/scimago.json') as f:
    data = json.load(f)
    
found = [r for r in data if test_id in r.get('identifiers', [])]
if found:
    print(f"✓ Found in JSON!")
    print(f"  Identifiers: {found[0]['identifiers']}")
    print(f"  Categories: {found[0]['categories']}")
    print(f"  Areas: {found[0]['areas']}")
else:
    print(f"✗ NOT found in JSON")

# 2. Check database
print("\n2. Checking database:")
conn = sqlite3.connect('./relational.db')

# Direct query
df = pd.read_sql_query(
    "SELECT * FROM categories WHERE identifiers = ?",
    conn,
    params=(test_id,)
)
print(f"Direct match (identifiers = '{test_id}'): {len(df)} rows")
if len(df) > 0:
    print(df.head())

# Fuzzy search
df2 = pd.read_sql_query(
    "SELECT * FROM categories WHERE identifiers LIKE ?",
    conn,
    params=(f"%{test_id}%",)
)
print(f"\nFuzzy match (identifiers LIKE '%{test_id}%'): {len(df2)} rows")
if len(df2) > 0:
    print(df2.head())

# Check what identifiers look like in the database
print("\n3. Sample identifiers in database:")
sample = pd.read_sql_query("SELECT DISTINCT identifiers FROM categories LIMIT 20", conn)
print(sample)

conn.close()

# 3. Test the handler methods
print("\n4. Testing CategoryQueryHandler methods:")
from impl import CategoryQueryHandler

cat_handler = CategoryQueryHandler()
cat_handler.setDbPathOrUrl('./relational.db')

result = cat_handler.getCategoriesByJournalId(test_id)
print(f"getCategoriesByJournalId('{test_id}'): {len(result)} rows")
if len(result) > 0:
    print(result)

result2 = cat_handler.getAreasByJournalId(test_id)
print(f"\ngetAreasByJournalId('{test_id}'): {len(result2)} rows")
if len(result2) > 0:
    print(result2)
