import json

# Load JSON and check for the area
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

area_to_check = 'Business, Management and Accounting'

# Get unique category IDs from JSON for this area
cats_for_area = set()
for rec in records:
    areas = rec.get('areas') or []
    if area_to_check in areas:
        for c in rec.get('categories', []) or []:
            cid = c.get('id')
            if cid:
                cats_for_area.add(cid)

print(f'Expected categories from JSON: {len(cats_for_area)}')
print(f'\nCategories: {sorted(cats_for_area)}')

# Now check the database
import sqlite3
import pandas as pd

conn = sqlite3.connect('relational.db')

# Using the same logic as the method
area = 'Business, Management and Accounting'
query = """
SELECT DISTINCT category_id 
FROM categories 
WHERE areas = ? 
   OR areas LIKE ?
   OR areas LIKE ?
   OR areas LIKE ?
"""
params = (
    area,  # exact match
    f"{area},%",  # at start
    f"%,{area},%",  # in middle
    f"%,{area}"  # at end
)
df = pd.read_sql_query(query, conn, params=params)
cats_from_db = set(df['category_id'].tolist())

print(f'\nActual categories from DB: {len(cats_from_db)}')
print(f'\nCategories: {sorted(cats_from_db)}')

# Find the difference
in_json_not_db = cats_for_area - cats_from_db
in_db_not_json = cats_from_db - cats_for_area

print(f'\nIn JSON but not in DB: {len(in_json_not_db)}')
if in_json_not_db:
    print(f'  {in_json_not_db}')
    
print(f'\nIn DB but not in JSON: {len(in_db_not_json)}')
if in_db_not_json:
    print(f'  {in_db_not_json}')

# Let's check if there's a category in the JSON that didn't get matched
if in_json_not_db:
    for cat in in_json_not_db:
        print(f'\nLooking for category "{cat}" in the database...')
        query2 = """
        SELECT category_id, areas
        FROM categories
        WHERE category_id = ?
        LIMIT 5
        """
        df2 = pd.read_sql_query(query2, conn, params=(cat,))
        print(df2)

conn.close()
