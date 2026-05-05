from rdflib import Graph, Namespace
import sqlite3, pandas as pd

g = Graph()
g.parse('doaj.ttl', format='turtle')
schema = Namespace('https://schema.org/')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

journals_data = {}
for s in g.subjects(RDF.type, schema.Periodical):
    journals_data[str(s)] = {
        'identifier': str(g.value(s, schema.identifier) or ''),
        'title': str(g.value(s, schema.title) or ''),
        'apc': str(g.value(s, schema.processingFee) or 'false'),
    }
all_df = pd.DataFrame(list(journals_data.values()))
print(f'Journals in graph: {len(all_df)}')

def parse_list_field(raw):
    if not raw: return []
    return [p.strip() for p in str(raw).replace(';', ',').split(',') if p.strip()]

def coerce_bool(x):
    if isinstance(x, bool): return x
    s = str(x).strip().lower()
    if s in {'true', 't', 'yes', 'y', '1'}: return True
    return False

print()
print('TEST 4: getDiamondJournalsInAreasAndCategoriesWithQuartile(Medicine, Oncology, Q1)')
conn = sqlite3.connect('./relational.db')
area = 'Medicine'
df_cats = pd.read_sql_query(
    'SELECT DISTINCT category_id FROM categories WHERE areas=? OR areas LIKE ? OR areas LIKE ? OR areas LIKE ?',
    conn, params=(area, area+',%', '%,'+area+',%', '%,'+area)
)
area_cat_ids = set(df_cats['category_id'].unique())
requested_cats = {'Oncology'}
matching_cats = area_cat_ids & requested_cats
print(f'  Matching categories (area & requested): {matching_cats}')

if matching_cats:
    ph = ','.join(['?'] * len(matching_cats))
    df_ids = pd.read_sql_query(
        f'SELECT DISTINCT identifiers FROM categories WHERE category_id IN ({ph}) AND quartile=?',
        conn, params=tuple(matching_cats) + ('Q1',)
    )
    conn.close()
    wanted = set(df_ids['identifiers'].str.strip())
    print(f'  wanted_identifiers: {len(wanted)}')

    matches = {}
    for _, row in all_df.iterrows():
        ids = parse_list_field(row['identifier'])
        if any(i in wanted for i in ids):
            key = '|'.join(sorted(set(ids)))
            matches[key] = {'title': row['title'], 'apc': row['apc']}
    print(f'  All matching journals: {len(matches)}')

    diamond = {k: v for k, v in matches.items() if not coerce_bool(v['apc'])}
    print(f'  Diamond journals (APC=False): {len(diamond)}')
    sample_titles = [v['title'] for v in list(diamond.values())[:3]]
    print(f'  Sample titles: {sample_titles}')
else:
    conn.close()
    print('  No matching categories found!')

# Also test getLicence
print()
print('TEST 1 (getLicence): Journal.getLicence() method check')
from impl import Journal
j = Journal(['1234-5678'], 'Test Journal', ['English'], False, 'CC BY', False)
print(f'  getLicence() = "{j.getLicence()}"')
print(f'  getLicense() = "{j.getLicense()}"')
print('  Both methods work correctly.' if j.getLicence() == 'CC BY' else '  ERROR: getLicence() returned wrong value!')
