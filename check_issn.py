import json
import sqlite3
import pandas as pd

# Load JSON to find the exact record
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

area_to_check = 'Business, Management and Accounting'

# Find record with Pollution and Business, Management and Accounting
for rec in records:
    areas = rec.get('areas') or []
    categories = rec.get('categories', []) or []
    
    has_pollution = any(c.get('id') == 'Pollution' for c in categories)
    has_area = area_to_check in areas
    
    if has_pollution and has_area:
        issn = rec.get('issn')
        print(f'Found JSON record:')
        print(f'  ISSN: {issn}')
        print(f'  Areas: {areas}')
        print(f'  Categories: {[c.get("id") for c in categories]}')
        
        # Now check if this ISSN exists in the database
        conn = sqlite3.connect('relational.db')
        
        # Check if we have this ISSN
        query1 = """
        SELECT DISTINCT identifiers, category_id, areas
        FROM categories
        WHERE identifiers = ?
        LIMIT 10
        """
        df1 = pd.read_sql_query(query1, conn, params=(issn,))
        print(f'\n  Database results for ISSN {issn}:')
        if df1.empty:
            print('    NOT FOUND')
        else:
            print(f'    Found {len(df1)} rows')
            for idx, row in df1.iterrows():
                print(f'      Category: {row["category_id"]}, Areas: {row["areas"]}')
        
        # Check if this ISSN is in the database with Pollution
        query2 = """
        SELECT identifiers, category_id, areas
        FROM categories
        WHERE identifiers = ?
          AND category_id = 'Pollution'
        """
        df2 = pd.read_sql_query(query2, conn, params=(issn,))
        print(f'\n  Pollution entries for this ISSN:')
        if df2.empty:
            print('    NOT FOUND')
        else:
            for idx, row in df2.iterrows():
                print(f'      Areas: {row["areas"]}')
        
        conn.close()
        break
