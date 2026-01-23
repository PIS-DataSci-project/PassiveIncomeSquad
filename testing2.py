# DEBUG: Test the query directly
print("\n=== DEBUGGING ===")
print("Testing direct SPARQL query...")

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
sparql = SPARQLWrapper(endpoint)

# Test query for 1983-9979
test_query = """
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
WHERE {
    ?journal rdf:type schema:Periodical .
    OPTIONAL { ?journal schema:title ?title }
    ?journal schema:identifier ?identifier .
    FILTER(CONTAINS(STR(?identifier), "1983-9979"))
    OPTIONAL { ?journal schema:inLanguage ?language }
    OPTIONAL { ?journal schema:publishedBy ?publisher }
    OPTIONAL { ?journal schema:award ?seal }
    OPTIONAL { ?journal schema:license ?license }
    OPTIONAL { ?journal schema:processingFee ?apc }
}
"""

sparql.setQuery(test_query)
sparql.setReturnFormat(JSON)

try:
    results = sparql.query().convert()
    print(f"Query returned {len(results['results']['bindings'])} results")
    
    if results['results']['bindings']:
        print("\nFirst result:")
        for key, value in results['results']['bindings'][0].items():
            print(f"  {key}: {value.get('value', 'N/A')}")
    else:
        print("No results found!")
        
        # Try a simpler query to see what identifiers actually look like
        print("\nChecking what identifiers are stored...")
        check_query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?identifier
        WHERE {
            ?journal schema:identifier ?identifier .
        }
        LIMIT 10
        """
        sparql.setQuery(check_query)
        results2 = sparql.query().convert()
        print("Sample identifiers in database:")
        for binding in results2['results']['bindings']:
            print(f"  - {binding['identifier']['value']}")
            
except Exception as e:
    print(f"Error: {e}")

print("=== END DEBUG ===\n")

# More comprehensive debug
print("\n=== FULL DATABASE CHECK ===")

# Check what properties journals actually have
check_query = """
PREFIX schema: <https://schema.org/>

SELECT ?journal ?title ?identifier
WHERE {
    ?journal a schema:Periodical .
    OPTIONAL { ?journal schema:title ?title }
    OPTIONAL { ?journal schema:identifier ?identifier }
}
LIMIT 20
"""

sparql.setQuery(check_query)
sparql.setReturnFormat(JSON)

try:
    results = sparql.query().convert()
    print(f"Found {len(results['results']['bindings'])} journals")
    
    has_identifier_count = 0
    for binding in results['results']['bindings']:
        title = binding.get('title', {}).get('value', 'NO TITLE')
        identifier = binding.get('identifier', {}).get('value', 'NO IDENTIFIER')
        if identifier != 'NO IDENTIFIER':
            has_identifier_count += 1
        print(f"Title: {title[:50]}... | ID: {identifier}")
    
    print(f"\nJournals with identifiers: {has_identifier_count}/{len(results['results']['bindings'])}")
    
except Exception as e:
    print(f"Error: {e}")

print("=== END CHECK ===\n")

# CLEAR THE DATABASE
print("\n=== CLEARING DATABASE ===")

from SPARQLWrapper import SPARQLWrapper, POST, DIGEST

endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
sparql = SPARQLWrapper(endpoint)

# Delete all triples
delete_query = """
DELETE WHERE { ?s ?p ?o }
"""

sparql.setQuery(delete_query)
sparql.setMethod(POST)

try:
    sparql.query()
    print("✓ Database cleared successfully!")
except Exception as e:
    print(f"✗ Error clearing database: {e}")

print("=== END CLEAR ===\n")

# RE-UPLOAD THE DATA
print("\n=== RE-UPLOADING DATA ===")

from impl import JournalUploadHandler
from os import sep

journal_csv = "data" + sep + "doaj-csv.csv"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

jou_upload = JournalUploadHandler()
jou_upload.setDbPathOrUrl(grp_endpoint)

print("Uploading journal data...")
try:
    result = jou_upload.pushDataToDb(journal_csv)
    if result:
        print("✓ Upload successful!")
    else:
        print("✗ Upload failed!")
except Exception as e:
    print(f"✗ Error during upload: {e}")

print("=== END UPLOAD ===\n")

# VERIFY THE FIX
print("\n=== VERIFYING FIX ===")

check_query = """
PREFIX schema: <https://schema.org/>

SELECT ?journal ?title ?identifier
WHERE {
    ?journal a schema:Periodical .
    OPTIONAL { ?journal schema:title ?title }
    OPTIONAL { ?journal schema:identifier ?identifier }
}
LIMIT 10
"""

sparql.setQuery(check_query)
sparql.setReturnFormat(JSON)

try:
    results = sparql.query().convert()
    print(f"Found {len(results['results']['bindings'])} journals")
    
    has_identifier_count = 0
    for binding in results['results']['bindings']:
        title = binding.get('title', {}).get('value', 'NO TITLE')
        identifier = binding.get('identifier', {}).get('value', 'NO IDENTIFIER')
        if identifier != 'NO IDENTIFIER':
            has_identifier_count += 1
        print(f"Title: {title[:50]}... | ID: {identifier}")
    
    print(f"\nJournals with identifiers: {has_identifier_count}/{len(results['results']['bindings'])}")
    
except Exception as e:
    print(f"Error: {e}")

print("=== END VERIFY ===\n")