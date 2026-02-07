import sqlite3
import pandas as pd

conn = sqlite3.connect('relational.db')

# Check sample rows with Business, Management and Accounting
query = """
SELECT DISTINCT category_id, areas 
FROM categories 
WHERE areas LIKE '%Business, Management and Accounting%' 
LIMIT 10
"""
df = pd.read_sql_query(query, conn)
print('Sample rows:')
print(df)

# Count unique categories with the area using LIKE
query2 = """
SELECT COUNT(DISTINCT category_id) as count
FROM categories 
WHERE areas LIKE '%Business, Management and Accounting%'
"""
result = pd.read_sql_query(query2, conn)
print('\nTotal categories with this area (LIKE):')
print(result)

# Now let's check with the exact matching logic from getCategoriesAssignedToAreas
area = 'Business, Management and Accounting'
query3 = """
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
df3 = pd.read_sql_query(query3, conn, params=params)
print(f'\nUsing exact matching logic: {len(df3)} categories')
print(df3.head(10))

# Let's see some examples of areas column
query4 = """
SELECT DISTINCT areas 
FROM categories 
WHERE areas LIKE '%Business, Management and Accounting%'
LIMIT 20
"""
df4 = pd.read_sql_query(query4, conn)
print('\nSample areas values:')
for idx, row in df4.iterrows():
    print(f"  '{row['areas']}'")

conn.close()
