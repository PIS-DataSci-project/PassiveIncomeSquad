import json

with open('data/scimago.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get first few records with 'Biochemistry'
count = 0
for record in data:
    cats = record.get('categories', [])
    for cat in cats:
        if isinstance(cat, dict) and cat.get('id') == 'Biochemistry':
            print(f'Record: {record.get("id")}')
            print(f'Areas: {record.get("areas")}')
            count += 1
            if count >= 3:
                break
    if count >= 3:
        break
