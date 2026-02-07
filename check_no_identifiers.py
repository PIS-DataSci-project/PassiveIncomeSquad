import json

# Count records with and without identifiers
with open('data/scimago.json', encoding='utf-8') as f:
    records = json.load(f)

total_records = len(records)
records_with_identifiers = 0
records_without_identifiers = 0
categories_skipped = set()

for rec in records:
    identifiers = rec.get('identifiers', [])
    
    # Normalize identifiers
    if identifiers is None:
        identifiers = []
    elif not isinstance(identifiers, list):
        identifiers = [identifiers]
    
    # Filter out None values
    identifiers = [i for i in identifiers if i is not None]
    
    if identifiers:
        records_with_identifiers += 1
    else:
        records_without_identifiers += 1
        # Track which categories are in records without identifiers
        categories = rec.get('categories', []) or []
        for c in categories:
            if isinstance(c, dict):
                cid = c.get('id')
                if cid:
                    categories_skipped.add(cid)

print(f'Total records in JSON: {total_records}')
print(f'Records with identifiers: {records_with_identifiers}')
print(f'Records without identifiers: {records_without_identifiers}')
print(f'\nCategories that appear in records without identifiers:')
print(f'  Count: {len(categories_skipped)}')
print(f'  Categories: {sorted(categories_skipped)}')

# Check if Pollution is only in records without identifiers
print('\n\nChecking Pollution specifically:')
pollution_with_id = 0
pollution_without_id = 0

for rec in records:
    identifiers = rec.get('identifiers', [])
    if identifiers is None:
        identifiers = []
    elif not isinstance(identifiers, list):
        identifiers = [identifiers]
    identifiers = [i for i in identifiers if i is not None]
    
    categories = rec.get('categories', []) or []
    has_pollution = any(c.get('id') == 'Pollution' for c in categories if isinstance(c, dict))
    
    if has_pollution:
        if identifiers:
            pollution_with_id += 1
        else:
            pollution_without_id += 1

print(f'  Pollution in records WITH identifiers: {pollution_with_id}')
print(f'  Pollution in records WITHOUT identifiers: {pollution_without_id}')
