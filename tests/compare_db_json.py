import json
import sqlite3

json_path = 'data/scimago.json'
db_path = './relational.db'

with open(json_path, encoding='utf-8') as f:
    records = json.load(f)

# categories from JSON
json_cats = set()
json_cat_quartiles = {}
json_areas = set()
for rec in records:
    for c in rec.get('categories', []) or []:
        cid = c.get('id')
        q = c.get('quartile')
        if cid:
            cid_s = cid.strip()
            json_cats.add(cid_s)
            json_cat_quartiles[cid_s] = q

    for a in rec.get('areas', []) or []:
        json_areas.add(a.strip())

# derived expected values used previously
quartiles_to_check = {'Q1','Q2'}
area_to_check = 'Biochemistry, Genetics and Molecular Biology'
category_to_check = 'Cell Biology'
expected_categories_with_quartile = len({cid for cid, q in json_cat_quartiles.items() if q in quartiles_to_check})
cats_for_area = set()
for rec in records:
    areas = rec.get('areas') or []
    if area_to_check in areas:
        for c in rec.get('categories', []) or []:
            cid = c.get('id')
            if cid:
                cats_for_area.add(cid.strip())
expected_categories_assigned_to_area = len(cats_for_area)
areas_for_category = set()
for rec in records:
    for c in rec.get('categories', []) or []:
        if c.get('id') == category_to_check:
            for a in rec.get('areas') or []:
                areas_for_category.add(a.strip())
expected_areas_assigned_to_category = len(areas_for_category)

# categories and areas from DB
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT DISTINCT category_id FROM categories")
db_cats = {row[0].strip() for row in cur.fetchall() if row[0] is not None}
cur.execute("SELECT DISTINCT areas FROM categories WHERE areas IS NOT NULL")
db_areas_raw = [row[0] for row in cur.fetchall()]
# split comma-separated areas into single names
db_areas = set()
for r in db_areas_raw:
    parts = [p.strip() for p in str(r).split(',') if p.strip()]
    db_areas.update(parts)

# counts
print('Counts:')
print(f' JSON unique categories: {len(json_cats)}')
print(f' DB unique categories:   {len(db_cats)}')
print(f' JSON unique areas:      {len(json_areas)}')
print(f' DB unique areas:        {len(db_areas)}')

# diffs
cats_in_db_not_json = sorted([c for c in db_cats if c not in json_cats])
cats_in_json_not_db = sorted([c for c in json_cats if c not in db_cats])
areas_in_db_not_json = sorted([a for a in db_areas if a not in json_areas])
areas_in_json_not_db = sorted([a for a in json_areas if a not in db_areas])

print('\nCategories in DB but not in JSON (sample up to 50):')
for c in cats_in_db_not_json[:50]:
    print(' -', c)

print('\nCategories in JSON but not in DB (sample up to 50):')
for c in cats_in_json_not_db[:50]:
    print(' -', c)

print('\nAreas in DB but not in JSON (sample up to 50):')
for a in areas_in_db_not_json[:50]:
    print(' -', a)

print('\nAreas in JSON but not in DB (sample up to 50):')
for a in areas_in_json_not_db[:50]:
    print(' -', a)

# show top DB categories by row count (could indicate duplicates)
cur.execute('SELECT category_id, COUNT(*) as cnt FROM categories GROUP BY category_id ORDER BY cnt DESC LIMIT 20')
print('\nTop 20 DB categories by row count:')
for row in cur.fetchall():
    print(f' {row[0]} : {row[1]}')

conn.close()

# Now compute actuals via CategoryQueryHandler to compare with expected
try:
    from impl import CategoryQueryHandler
    qh = CategoryQueryHandler(dbPathOrUrl=db_path)
    df_all_cats = qh.getAllCategories()
    actual_all_categories = len(df_all_cats)
    actual_all_areas = len(qh.getAllAreas())
    df_quart = qh.getCategoriesWithQuartile(quartiles_to_check)
    actual_categories_with_quartile = len(df_quart)
    actual_categories_assigned_to_area = len(qh.getCategoriesAssignedToAreas({area_to_check}))
    actual_areas_assigned_to_category = len(qh.getAreasAssignedToCategories({category_to_check}))

    print('\nSample of CategoryQueryHandler.getAllCategories() DataFrame:')
    try:
        print(df_all_cats.head())
        if 'category_id' in df_all_cats.columns:
            print(' unique category_id in df_all_cats:', df_all_cats['category_id'].nunique())
    except Exception:
        print('Could not print df sample')

    print('\nSample of getCategoriesWithQuartile() DataFrame:')
    try:
        print(df_quart.head())
    except Exception:
        print('Could not print quartile df')

    print('\nSummary comparison (expected from JSON vs actual from DB handlers):')
    print(f' getAllCategories: expected={len(json_cats)}, actual={actual_all_categories}, match={len(json_cats)==actual_all_categories}')
    print(f' getAllAreas: expected={len(json_areas)}, actual={actual_all_areas}, match={len(json_areas)==actual_all_areas}')
    print(f' getCategoriesWithQuartile({quartiles_to_check}): expected={expected_categories_with_quartile}, actual={actual_categories_with_quartile}, match={expected_categories_with_quartile==actual_categories_with_quartile}')
    print(f" getCategoriesAssignedToAreas('{area_to_check}'): expected={expected_categories_assigned_to_area}, actual={actual_categories_assigned_to_area}, match={expected_categories_assigned_to_area==actual_categories_assigned_to_area}")
    print(f" getAreasAssignedToCategories('{category_to_check}'): expected={expected_areas_assigned_to_category}, actual={actual_areas_assigned_to_category}, match={expected_areas_assigned_to_category==actual_areas_assigned_to_category}")
except Exception as e:
    print('\nCould not import/run CategoryQueryHandler:', e)
