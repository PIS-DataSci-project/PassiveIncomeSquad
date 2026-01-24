import pandas as pd
import json
import sqlite3

# Check DOAJ CSV
print("=" * 60)
print("CHECKING DOAJ CSV")
print("=" * 60)
df = pd.read_csv('data/doaj-csv.csv')
result = df[
    df['Journal ISSN (print version)'].astype(str).str.contains('2224-9281', na=False) | 
    df['Journal EISSN (online version)'].astype(str).str.contains('2224-9281', na=False)
]
print(f'Found {len(result)} records with 2224-9281')
if len(result) > 0:
    print('\nFirst match:')
    print('Title:', result.iloc[0]['Journal title'])
    print('ISSN:', result.iloc[0]['Journal ISSN (print version)'])
    print('EISSN:', result.iloc[0]['Journal EISSN (online version)'])

# Check Scimago JSON
print("\n" + "=" * 60)
print("CHECKING SCIMAGO JSON")
print("=" * 60)
with open('data/scimago-json.json') as f:
    data = json.load(f)
    
found = [r for r in data if '2224-9281' in r.get('identifiers', [])]
print(f'Found {len(found)} records with 2224-9281 in scimago')

# Check database
print("\n" + "=" * 60)
print("CHECKING DATABASE")
print("=" * 60)
try:
    conn = sqlite3.connect('./relational.db')
    
    # Check if table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")
    
    # Check categories table
    df_db = pd.read_sql_query("SELECT * FROM categories WHERE identifiers = '2224-9281'", conn)
    print(f"\nRows with identifier '2224-9281': {len(df_db)}")
    if len(df_db) > 0:
        print(df_db)
    
    # Show sample identifiers
    print("\nSample identifiers in database:")
    sample = pd.read_sql_query("SELECT DISTINCT identifiers FROM categories LIMIT 10", conn)
    print(sample)
    
    # Count total rows
    count = pd.read_sql_query("SELECT COUNT(*) as count FROM categories", conn)
    print(f"\nTotal rows in categories table: {count.iloc[0]['count']}")
    
    conn.close()
except Exception as e:
    print(f"Error accessing database: {e}")
