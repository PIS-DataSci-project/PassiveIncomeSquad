import json

data = json.load(open('data/scimago.json', encoding='utf-8'))

found = [rec for rec in data if 'Materials Science' in (rec.get('areas') or []) 
         and any(c.get('id') == 'Human-Computer Interaction' for c in (rec.get('categories') or []))]

print(f'Journals with Materials Science area AND Human-Computer Interaction category: {len(found)}')

for rec in found:
    print(f"\nJournal: {rec.get('title', 'N/A')}")
    print(f"Areas: {rec.get('areas')}")
    cats = [c for c in rec.get('categories', []) if c.get('id') == 'Human-Computer Interaction']
    print(f"Human-Computer Interaction quartile: {cats[0].get('quartile') if cats else 'N/A'}")
    
    # Check if category has its own areas
    for c in rec.get('categories', []):
        if c.get('id') == 'Human-Computer Interaction':
            if 'areas' in c:
                print(f"Category has its own areas: {c.get('areas')}")
