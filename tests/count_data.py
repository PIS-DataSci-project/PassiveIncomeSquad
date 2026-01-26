import pandas as pd
import json

# Count journals
df = pd.read_csv('data/doaj.csv')
print(f'Total journals in doaj.csv: {len(df)}')

# Count categories and areas
with open('data/scimago.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f'Total records in scimago.json: {len(data)}')

categories = set()
areas = set()

for record in data:
    cats = record.get('categories', [])
    if isinstance(cats, list):
        for cat in cats:
            if isinstance(cat, dict) and 'id' in cat:
                categories.add(cat['id'])
    
    record_areas = record.get('areas')
    if isinstance(record_areas, list):
        areas.update(record_areas)

print(f'Unique categories: {len(categories)}')
print(f'Unique areas: {len(areas)}')
