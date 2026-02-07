import json
import sqlite3
import pandas as pd

# Load JSON to find where Pollution has Business, Management and Accounting
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

area_to_check = 'Business, Management and Accounting'

# Find records where Pollution is a category and this area is present
found = False
for rec in records:
    areas = rec.get('areas') or []
    categories = rec.get('categories', []) or []
    
    has_pollution = any(c.get('id') == 'Pollution' for c in categories)
    has_area = area_to_check in areas
    
    if has_pollution and has_area:
        found = True
        print(f'Found record with Pollution and {area_to_check}:')
        print(f'  Title: {rec.get("title", "N/A")}')
        print(f'  ISSN: {rec.get("issn", "N/A")}')
        print(f'  Areas: {areas}')
        print(f'  Categories:')
        for c in categories:
            print(f'    - {c.get("id")}: Q{c.get("quartile", "N/A")}')
        print()

if not found:
    print(f'No records found with Pollution and {area_to_check}')

# Now check in the database
print('\nChecking database for Pollution with this area...')
conn = sqlite3.connect('relational.db')
query = """
SELECT category_id, areas, identifiers
FROM categories
WHERE category_id = 'Pollution'
  AND (areas LIKE '%Business, Management and Accounting%')
"""
df = pd.read_sql_query(query, conn)
print(f'Found {len(df)} rows')
if not df.empty:
    for idx, row in df.iterrows():
        print(f"\nRow {idx+1}:")
        print(f"  Category: {row['category_id']}")
        print(f"  Areas: {row['areas']}")
        print(f"  ISSN: {row['identifiers']}")

# Let's also check all Pollution rows
print('\n\nAll Pollution rows in database:')
query2 = """
SELECT DISTINCT areas
FROM categories
WHERE category_id = 'Pollution'
"""
df2 = pd.read_sql_query(query2, conn)
print(f'Total unique area combinations for Pollution: {len(df2)}')
for idx, row in df2.iterrows():
    print(f"  {row['areas']}")

conn.close()
