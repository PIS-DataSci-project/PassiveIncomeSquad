import json

# Check for records with None quartiles
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

none_quartile_count = 0
categories_with_none_quartile = set()

for rec in records:
    categories = rec.get('categories', []) or []
    
    for c in categories:
        if isinstance(c, dict):
            quartile = c.get('quartile')
            if quartile is None:
                none_quartile_count += 1
                cat_id = c.get('id')
                if cat_id:
                    categories_with_none_quartile.add(cat_id)

print(f'Total category entries with None quartile: {none_quartile_count}')
print(f'Unique categories with None quartile: {len(categories_with_none_quartile)}')
print(f'\nSample categories: {sorted(list(categories_with_none_quartile))[:20]}')

# Check if this affects our specific case
area_to_check = 'Business, Management and Accounting'
cats_with_none_q = set()

for rec in records:
    areas = rec.get('areas') or []
    if area_to_check not in areas:
        continue
    
    categories = rec.get('categories', []) or []
    for c in categories:
        if isinstance(c, dict):
            quartile = c.get('quartile')
            if quartile is None:
                cat_id = c.get('id')
                if cat_id:
                    cats_with_none_q.add(cat_id)

print(f'\n\nCategories with None quartile for area "{area_to_check}":')
print(f'  Count: {len(cats_with_none_q)}')
print(f'  Categories: {sorted(cats_with_none_q)}')
