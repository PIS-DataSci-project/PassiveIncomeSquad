from impl import JournalUploadHandler
import os
import requests
from rdflib import Graph, URIRef, RDF

# Create handler instance
handler = JournalUploadHandler()

# Verify CSV exists
csv_path = "data/doaj-csv.csv"
if not os.path.exists(csv_path):
    print(f"✗ CSV file not found: {csv_path}")
    exit(1)

# Set the Blazegraph SPARQL endpoint
db_url = "http://127.0.0.1:9999/blazegraph/sparql" # same for everybody
if handler.setDbPathOrUrl(db_url):
    print(f"✓ Database URL set to: {handler.getDbPathOrUrl()}")
else:
    print("✗ Failed to set database URL")
    exit(1)

# Check Blazegraph accessibility
try:
    response = requests.get(db_url)
    print(f"✓ Blazegraph is accessible")
except:
    print(f"✗ Cannot reach Blazegraph at {db_url}")
    exit(1)

# Test creating graph first
print("\nTesting graph creation...")
try:
    graph = handler.createGraph(csv_path)
    triple_count = len(list(graph))  # Proper way to count RDF triples
    print(f"✓ Graph created with {triple_count} triples")
    
    # Show sample triples
    print("\nSample triples (first 5):")
    for i, triple in enumerate(graph.triples((None, None, None))):
        if i < 5:
            print(f"  {i+1}. {triple}")
        else:
            break
except FileNotFoundError as e:
    print(f"✗ File error: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Error creating graph: {e}")
    exit(1)

# Check for existing data before uploading
def check_existing_data(endpoint):
    """Query Blazegraph to count existing journal records"""
    query = """
    PREFIX schema: <https://schema.org/>
    SELECT (COUNT(?journal) as ?count)
    WHERE {
        ?journal a schema:Periodical .
    }
    """
    try:
        from SPARQLWrapper import SPARQLWrapper, JSON
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        count = int(results["results"]["bindings"][0]["count"]["value"])
        return count
    except Exception as e:
        print(f"  Warning: Could not check existing data: {e}")
        return None

print("\nChecking for existing data in Blazegraph...")
existing_count = check_existing_data(db_url)
if existing_count is not None:
    if existing_count > 0:
        print(f"⚠ Warning: {existing_count} journals already exist in database")
        print("  This may indicate duplicate data if you upload again.")
        confirm = input("  Continue with upload? (yes/no): ")
        if confirm.lower() != "yes":
            print("✗ Upload cancelled")
            exit(1)
    else:
        print(f"✓ Database is empty - safe to upload")

# Push data to database
print("\nPushing data to Blazegraph...")
try:
    result = handler.pushDataToDb(csv_path)
    if result:
        print("✓ Data pushed to database successfully!")
        
        # Verify upload
        print("\nVerifying upload...")
        new_count = check_existing_data(db_url)
        if new_count is not None:
            print(f"✓ Total journals in database: {new_count}")
    else:
        print("✗ Failed to push data")
except ConnectionError as e:
    print(f"✗ Connection error (is Blazegraph running?): {e}")
except Exception as e:
    print(f"✗ Error pushing data: {e}")    
    
# ================================

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