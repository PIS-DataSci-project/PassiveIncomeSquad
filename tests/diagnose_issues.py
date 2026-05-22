import sqlite3, pandas as pd, json
from rdflib import Graph, Namespace

g = Graph()
g.parse('doaj.ttl', format='turtle')
schema = Namespace('https://schema.org/')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

def parse_ids(raw):
    if not raw: return []
    return [p.strip() for p in str(raw).replace(';',',').split(',') if p.strip()]

known_areas = {
    'Agricultural and Biological Sciences','Arts and Humanities',
    'Biochemistry, Genetics and Molecular Biology','Business, Management and Accounting',
    'Chemical Engineering','Chemistry','Computer Science','Decision Sciences',
    'Dentistry','Earth and Planetary Sciences','Economics, Econometrics and Finance',
    'Energy','Engineering','Environmental Science','Health Professions',
    'Immunology and Microbiology','Materials Science','Mathematics','Medicine',
    'Multidisciplinary','Neuroscience','Nursing',
    'Pharmacology, Toxicology and Pharmaceutics','Physics and Astronomy',
    'Psychology','Social Sciences','Veterinary'
}

def parse_areas_from_str(areas_str):
    parsed = set()
    remaining = areas_str
    for area in sorted(known_areas, key=len, reverse=True):
        while area in remaining:
            parsed.add(area)
            remaining = remaining.replace(area, '', 1).lstrip(',').strip()
    return parsed

with open('data/scimago.json', encoding='utf-8') as f:
    scimago = json.load(f)

print("="*60)
print("ISSUE 1: getEntityById areas check")
print("="*60)

entity_id = '2532-8816'
matched_journals = []
for s in g.subjects(RDF.type, schema.Periodical):
    id_val = str(g.value(s, schema.identifier) or '')
    if entity_id in id_val:
        matched_journals.append({'uri': str(s), 'identifier': id_val, 'title': str(g.value(s, schema.title) or '')})

print(f'SPARQL CONTAINS matches for {entity_id}: {len(matched_journals)}')
for j in matched_journals:
    print(f'  title={j["title"]}, identifier={j["identifier"]}')

if matched_journals:
    first = matched_journals[0]
    id_str = first['identifier']
    split_ids = [i.strip() for i in id_str.split(';') if i.strip()]
    print(f'Split identifiers for area lookup: {split_ids}')

    conn = sqlite3.connect('relational.db')
    all_areas_impl = set()
    for jid in split_ids:
        q = 'SELECT DISTINCT areas FROM categories WHERE identifiers = ? AND areas IS NOT NULL'
        df = pd.read_sql_query(q, conn, params=(jid,))
        for _, row in df.iterrows():
            all_areas_impl |= parse_areas_from_str(row['areas'])
    conn.close()

    expected_areas = set()
    for rec in scimago:
        ids = rec.get('identifiers', []) or []
        for sid in ids:
            if str(sid).strip() in split_ids:
                for a in (rec.get('areas', []) or []):
                    expected_areas.add(str(a).strip())

    print(f'Impl areas:     {sorted(all_areas_impl)}')
    print(f'Expected areas: {sorted(expected_areas)}')
    print(f'Match: {all_areas_impl == expected_areas}')
    if all_areas_impl != expected_areas:
        print(f'  EXTRA:   {all_areas_impl - expected_areas}')
        print(f'  MISSING: {expected_areas - all_areas_impl}')

print()
print("="*60)
print("ISSUE 2: getJournalsInCategoriesWithQuartile identifier count")
print("="*60)

# Test: Oncology, Q1
cat_ids = {'Oncology'}
quartiles = {'Q1'}
conn = sqlite3.connect('relational.db')
ph_c = ','.join(['?']*len(cat_ids))
ph_q = ','.join(['?']*len(quartiles))
q = f'SELECT DISTINCT identifiers FROM categories WHERE category_id IN ({ph_c}) AND quartile IN ({ph_q})'
df = pd.read_sql_query(q, conn, params=tuple(cat_ids)+tuple(quartiles))
wanted = set(df['identifiers'].str.strip())
conn.close()
print(f'wanted_identifiers (DB): {len(wanted)}')

journal_map = {}
for s in g.subjects(RDF.type, schema.Periodical):
    id_val = str(g.value(s, schema.identifier) or '')
    ids = parse_ids(id_val)
    if not any(i in wanted for i in ids): continue
    key = '|'.join(sorted(set(ids)))
    journal_map[key] = ids

# Apply filter (as impl does)
all_filtered_ids = set()
for key, ids in journal_map.items():
    for i in ids:
        if i in wanted:
            all_filtered_ids.add(i)

print(f'Journals matched: {len(journal_map)}')
print(f'Unique IDs after filter: {len(all_filtered_ids)}')
# The "expected" by scimago = how many distinct identifiers are in DB
# The "actual" from impl = unique IDs after filter
print(f'Discrepancy (actual - expected): {len(all_filtered_ids) - len(wanted)}')

# ALSO check: unique IDs if we DON'T apply the filter
all_unfiltered_ids = set()
for key, ids in journal_map.items():
    for i in ids:
        all_unfiltered_ids.add(i)
print(f'Unique IDs WITHOUT filter: {len(all_unfiltered_ids)}')
print(f'Discrepancy without filter: {len(all_unfiltered_ids) - len(wanted)}')

print()
print("="*60)
print("ISSUE 3: getJournalsInAreasWithLicense journal count")
print("="*60)
area = 'Computer Science'
license_val = 'CC BY'
conn = sqlite3.connect('relational.db')
q_direct = '''SELECT DISTINCT identifiers FROM categories
              WHERE (areas = ? OR areas LIKE ? OR areas LIKE ? OR areas LIKE ?)
              AND identifiers IS NOT NULL'''
df_direct = pd.read_sql_query(q_direct, conn,
    params=(area, area+',%', '%,'+area+',%', '%,'+area))
wanted_direct = set(df_direct['identifiers'].str.strip())
conn.close()
print(f'wanted_identifiers (area direct): {len(wanted_direct)}')

j_direct = {}
for s in g.subjects(RDF.type, schema.Periodical):
    lic = str(g.value(s, schema.license) or '')
    if lic != license_val: continue
    id_val = str(g.value(s, schema.identifier) or '')
    ids = parse_ids(id_val)
    if not any(i in wanted_direct for i in ids): continue
    key = '|'.join(sorted(set(ids)))
    j_direct[key] = str(g.value(s, schema.title) or '')

print(f'Journals returned (current impl): {len(j_direct)}')

# Now check with expected: journals where ALL their identifiers are in area
j_strict = {}
for s in g.subjects(RDF.type, schema.Periodical):
    lic = str(g.value(s, schema.license) or '')
    if lic != license_val: continue
    id_val = str(g.value(s, schema.identifier) or '')
    ids = parse_ids(id_val)
    if not ids: continue
    # STRICT: ALL identifiers must be in wanted
    if all(i in wanted_direct for i in ids):
        key = '|'.join(sorted(set(ids)))
        j_strict[key] = str(g.value(s, schema.title) or '')

print(f'Journals returned (strict - ALL ids in area): {len(j_strict)}')
print(f'Extra journals in current impl vs strict: {len(j_direct) - len(j_strict)}')

# Journals in current but not strict (they have 1 ID in area, 1 not)
extra_journals = {k: v for k, v in j_direct.items() if k not in j_strict}
print(f'\nExtra journals (have some IDs not in area):')
for key, title in list(extra_journals.items())[:5]:
    ids = key.split('|')
    in_area = [i for i in ids if i in wanted_direct]
    not_in_area = [i for i in ids if i not in wanted_direct]
    print(f'  {title[:50]}: in_area={in_area}, not_in_area={not_in_area}')
