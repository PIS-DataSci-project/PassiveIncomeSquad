import json
import sqlite3
import pandas as pd

# Find the record with Pollution and Business, Management and Accounting
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

area_to_check = 'Business, Management and Accounting'

for rec in records:
    areas = rec.get('areas') or []
    categories = rec.get('categories', []) or []
    
    has_pollution = any(c.get('id') == 'Pollution' for c in categories if isinstance(c, dict))
    has_area = area_to_check in areas
    
    if has_pollution and has_area:
        print('Found JSON record with Pollution + Business, Management and Accounting:')
        print(f'  Identifiers: {rec.get("identifiers")}')
        print(f'  Areas: {areas}')
        print(f'  Categories:')
        for c in categories:
            if isinstance(c, dict):
                print(f'    - {c.get("id")}: Q{c.get("quartile")}')
        
        # Get the identifier(s)
        identifiers = rec.get('identifiers', [])
        if identifiers is None:
            identifiers = []
        elif not isinstance(identifiers, list):
            identifiers = [identifiers]
        
        print(f'\n  Processing identifiers: {identifiers}')
        
        # Check each identifier in the database
        conn = sqlite3.connect('relational.db')
        
        for identifier in identifiers:
            if identifier is None:
                continue
            
            print(f'\n  Checking identifier: {identifier}')
            
            # Check all categories for this identifier
            query1 = """
            SELECT category_id, areas
            FROM categories
            WHERE identifiers = ?
            ORDER BY category_id
            """
            df1 = pd.read_sql_query(query1, conn, params=(str(identifier),))
            print(f'    Total categories for this identifier: {len(df1)}')
            
            # Check specifically for Pollution
            query2 = """
            SELECT category_id, quartile, areas
            FROM categories
            WHERE identifiers = ?
              AND category_id = 'Pollution'
            """
            df2 = pd.read_sql_query(query2, conn, params=(str(identifier),))
            if df2.empty:
                print(f'    Pollution NOT FOUND for this identifier')
            else:
                print(f'    Pollution entries:')
                for idx, row in df2.iterrows():
                    print(f'      Q{row["quartile"]}, Areas: {row["areas"]}')
        
        conn.close()
        break
