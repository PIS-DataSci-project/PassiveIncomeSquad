import json
from impl import CategoryQueryHandler

# Config
scimago_path = 'data/scimago.json'
rel_db = './relational.db'

# Load JSON and compute expected counts
with open(scimago_path, encoding='utf-8') as f:
    records = json.load(f)

# Unique category ids and areas from JSON
unique_categories = set()
unique_areas = set()
all_category_ids = set()
all_area_names = set()

for rec in records:
    cats = rec.get('categories', []) or []
    for c in cats:
        cid = c.get('id')
        q = c.get('quartile')
        if cid:
            unique_categories.add((cid, q))
            all_category_ids.add(cid)
    areas = rec.get('areas') or []
    for a in areas:
        unique_areas.add(a)
        all_area_names.add(a)

# Get actual counts via CategoryQueryHandler
qh = CategoryQueryHandler(dbPathOrUrl=rel_db)

# Test set 1: Basic functionality (original test)
print('=' * 70)
print('TEST SET 1: Basic functionality')
print('=' * 70)

quartiles_to_check = {'Q1','Q2'}
area_to_check = 'Biochemistry, Genetics and Molecular Biology'
category_to_check = 'Cell Biology'

expected_all_categories = len({cid for cid, _ in unique_categories})
expected_all_areas = len(unique_areas)
expected_categories_with_quartile = len({cid for cid, q in unique_categories if q in quartiles_to_check})

cats_for_area = set()
for rec in records:
    areas = rec.get('areas') or []
    if area_to_check in areas:
        for c in rec.get('categories', []) or []:
            cid = c.get('id')
            if cid:
                cats_for_area.add(cid)
expected_categories_assigned_to_area = len(cats_for_area)

areas_for_category = set()
for rec in records:
    for c in rec.get('categories', []) or []:
        if c.get('id') == category_to_check:
            for a in rec.get('areas') or []:
                areas_for_category.add(a)
expected_areas_assigned_to_category = len(areas_for_category)

actual_all_categories = len(qh.getAllCategories())
actual_all_areas = len(qh.getAllAreas())
actual_categories_with_quartile = len(qh.getCategoriesWithQuartile(quartiles_to_check))
actual_categories_assigned_to_area = len(qh.getCategoriesAssignedToAreas({area_to_check}))
actual_areas_assigned_to_category = len(qh.getAreasAssignedToCategories({category_to_check}))

print(f'getAllCategories: expected={expected_all_categories}, actual={actual_all_categories}, match={expected_all_categories==actual_all_categories}')
print(f'getAllAreas: expected={expected_all_areas}, actual={actual_all_areas}, match={expected_all_areas==actual_all_areas}')
print(f"getCategoriesWithQuartile({quartiles_to_check}): expected={expected_categories_with_quartile}, actual={actual_categories_with_quartile}, match={expected_categories_with_quartile==actual_categories_with_quartile}")
print(f"getCategoriesAssignedToAreas('{area_to_check}'): expected={expected_categories_assigned_to_area}, actual={actual_categories_assigned_to_area}, match={expected_categories_assigned_to_area==actual_categories_assigned_to_area}")
print(f"getAreasAssignedToCategories('{category_to_check}'): expected={expected_areas_assigned_to_category}, actual={actual_areas_assigned_to_category}, match={expected_areas_assigned_to_category==actual_areas_assigned_to_category}")

# Test set 2: Different quartiles
print('\n' + '=' * 70)
print('TEST SET 2: Different quartiles')
print('=' * 70)

test_quartiles = [
    {'Q1'},
    {'Q3'},
    {'Q4'},
    {'Q1', 'Q3'},
    {'Q2', 'Q4'}
]

for quartiles in test_quartiles:
    expected = len({cid for cid, q in unique_categories if q in quartiles})
    actual = len(qh.getCategoriesWithQuartile(quartiles))
    match = expected == actual
    print(f"getCategoriesWithQuartile({quartiles}): expected={expected}, actual={actual}, match={match}")

# Test set 3: Different areas
print('\n' + '=' * 70)
print('TEST SET 3: Different areas (first 5 unique areas)')
print('=' * 70)

test_areas = list(all_area_names)[:5]
for area in test_areas:
    cats_for_area = set()
    for rec in records:
        areas = rec.get('areas') or []
        if area in areas:
            for c in rec.get('categories', []) or []:
                cid = c.get('id')
                if cid:
                    cats_for_area.add(cid)
    expected = len(cats_for_area)
    actual = len(qh.getCategoriesAssignedToAreas({area}))
    match = expected == actual
    print(f"getCategoriesAssignedToAreas('{area}'): expected={expected}, actual={actual}, match={match}")

# Test set 4: Different categories
print('\n' + '=' * 70)
print('TEST SET 4: Different categories (first 5 unique categories)')
print('=' * 70)

test_categories = list(all_category_ids)[:5]
for category in test_categories:
    areas_for_category = set()
    for rec in records:
        for c in rec.get('categories', []) or []:
            if c.get('id') == category:
                for a in rec.get('areas') or []:
                    areas_for_category.add(a)
    expected = len(areas_for_category)
    actual = len(qh.getAreasAssignedToCategories({category}))
    match = expected == actual
    print(f"getAreasAssignedToCategories('{category}'): expected={expected}, actual={actual}, match={match}")

# Test set 5: Multiple areas
print('\n' + '=' * 70)
print('TEST SET 5: Multiple areas')
print('=' * 70)

test_area_sets = [
    {'Arts and Humanities', 'Chemistry'},
    {'Computer Science', 'Mathematics'},
    {'Medicine', 'Physics and Astronomy'}
]

for area_set in test_area_sets:
    cats_for_areas = set()
    for rec in records:
        areas = rec.get('areas') or []
        if any(a in areas for a in area_set):
            for c in rec.get('categories', []) or []:
                cid = c.get('id')
                if cid:
                    cats_for_areas.add(cid)
    expected = len(cats_for_areas)
    actual = len(qh.getCategoriesAssignedToAreas(area_set))
    match = expected == actual
    print(f"getCategoriesAssignedToAreas({area_set}): expected={expected}, actual={actual}, match={match}")

print('\n' + '=' * 70)
print('ALL TESTS COMPLETED')
print('=' * 70)
