"""
Simulate mashup queries end-to-end without Blazegraph,
using rdflib native SPARQL on the local doaj.ttl file.
"""
from rdflib import Graph, Namespace
import sqlite3, pandas as pd

# Load TTL into rdflib graph
g = Graph()
g.parse('doaj.ttl', format='turtle')
print(f'Graph loaded: {len(g)} triples')

# Run the same getAllJournals SPARQL query
sparql_q = """
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
WHERE {
    ?journal rdf:type schema:Periodical .
    OPTIONAL { ?journal schema:title ?title }
    OPTIONAL { ?journal schema:identifier ?identifier }
    OPTIONAL { ?journal schema:inLanguage ?language }
    OPTIONAL { ?journal schema:publishedBy ?publisher }
    OPTIONAL { ?journal schema:award ?seal }
    OPTIONAL { ?journal schema:license ?license }
    OPTIONAL { ?journal schema:processingFee ?apc }
}
"""
results = list(g.query(sparql_q))
print(f'getAllJournals results: {len(results)} rows')

# Convert to DataFrame (same as _execute_sparql_query would do via HTTP)
rows = []
for row in results:
    rows.append({
        'journal': str(row[0]) if row[0] else '',
        'title': str(row[1]) if row[1] else '',
        'identifier': str(row[2]) if row[2] else '',
        'language': str(row[3]) if row[3] else '',
        'publisher': str(row[4]) if row[4] else '',
        'seal': str(row[5]) if row[5] else 'false',
        'license': str(row[6]) if row[6] else '',
        'apc': str(row[7]) if row[7] else 'false',
    })
all_df = pd.DataFrame(rows)
print(f'DataFrame shape: {all_df.shape}')
print(f'Sample identifiers: {all_df["identifier"].head(5).tolist()}')

# Matching helper
def parse_list_field(raw):
    if raw is None: return []
    text = str(raw).strip()
    if not text: return []
    text = text.replace(';', ',')
    return [p.strip() for p in text.split(',') if p.strip()]

# ------- TEST 1: getJournalsInCategoriesWithQuartile -------
print('\n--- TEST 1: getJournalsInCategoriesWithQuartile ---')
conn = sqlite3.connect('./relational.db')
category_ids = ('Artificial Intelligence', 'Oncology')
quartiles = ('Q1',)
placeholders_cat = ','.join(['?'] * len(category_ids))
placeholders_quart = ','.join(['?'] * len(quartiles))
query = f"""
SELECT DISTINCT identifiers FROM categories
WHERE category_id IN ({placeholders_cat})
  AND quartile IN ({placeholders_quart})
"""
df_sqlite = pd.read_sql_query(query, conn, params=category_ids + quartiles)
conn.close()
wanted = set(df_sqlite['identifiers'].str.strip())
print(f'wanted_identifiers: {len(wanted)}')

journal_map = {}
for _, row in all_df.iterrows():
    row_ids = parse_list_field(row['identifier'])
    if not row_ids: continue
    if not any(rid in wanted for rid in row_ids): continue
    key = '|'.join(sorted(set(row_ids)))
    if key not in journal_map:
        journal_map[key] = row['title']

print(f'Matching journals: {len(journal_map)}')
print('Sample titles:', list(journal_map.values())[:3])

# ------- TEST 2: getJournalsInAreasWithLicense -------
print('\n--- TEST 2: getJournalsInAreasWithLicense ---')
# Get categories in Medicine area
conn = sqlite3.connect('./relational.db')
area = 'Medicine'
q_area = """
SELECT DISTINCT category_id FROM categories
WHERE areas = ? OR areas LIKE ? OR areas LIKE ? OR areas LIKE ?
"""
df_cats = pd.read_sql_query(q_area, conn, params=(area, f'{area},%', f'%,{area},%', f'%,{area}'))
cat_ids = set(df_cats['category_id'].unique())
print(f'Categories in Medicine: {len(cat_ids)}')

# Get identifiers for those categories
if cat_ids:
    ph = ','.join(['?'] * len(cat_ids))
    df_ids = pd.read_sql_query(f'SELECT DISTINCT identifiers FROM categories WHERE category_id IN ({ph})', conn, params=tuple(cat_ids))
    wanted2 = set(df_ids['identifiers'].str.strip())
    print(f'wanted_identifiers: {len(wanted2)}')
conn.close()

# Get CC BY journals from graph
license_q = """
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
WHERE {
    ?journal rdf:type schema:Periodical .
    OPTIONAL { ?journal schema:title ?title }
    ?journal schema:license ?license .
    FILTER(?license = "CC BY")
    OPTIONAL { ?journal schema:identifier ?identifier }
    OPTIONAL { ?journal schema:inLanguage ?language }
    OPTIONAL { ?journal schema:publishedBy ?publisher }
    OPTIONAL { ?journal schema:award ?seal }
    OPTIONAL { ?journal schema:processingFee ?apc }
}
"""
lic_results = list(g.query(license_q))
print(f'CC BY journals in graph: {len(lic_results)}')

lic_rows = []
for row in lic_results:
    lic_rows.append({'identifier': str(row[2]) if row[2] else '', 'title': str(row[1]) if row[1] else ''})
lic_df = pd.DataFrame(lic_rows)

# Match
journal_map2 = {}
for _, row in lic_df.iterrows():
    row_ids = parse_list_field(row['identifier'])
    if not row_ids: continue
    if not any(rid in wanted2 for rid in row_ids): continue
    key = '|'.join(sorted(set(row_ids)))
    if key not in journal_map2:
        journal_map2[key] = row['title']

print(f'getJournalsInAreasWithLicense result: {len(journal_map2)}')
print('Sample:', list(journal_map2.values())[:3])

# ------- TEST 3: getLicence on a Journal -------
print('\n--- TEST 3: getLicence method ---')
from impl import Journal
j = Journal(['1234-5678'], 'Test Journal', ['English'], False, 'CC BY', False)
print(f'getLicence() = {j.getLicence()}')
print(f'getLicense() = {j.getLicense()}')
