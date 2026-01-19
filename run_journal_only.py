from Handlers import JournalUploadHandler
import os
import requests

# Create handler instance
handler = JournalUploadHandler()

# Verify CSV exists
csv_path = "data/doaj-csv.csv"
if not os.path.exists(csv_path):
    print(f"✗ CSV file not found: {csv_path}")
    exit(1)

# Set the Blazegraph SPARQL endpoint
db_url = "http://127.0.0.1:9999/blazegraph/sparql" # same for everybody
if handler.setdbPathOrUrl(db_url):
    print(f"✓ Database URL set to: {handler.getdbPathOrUrl()}")
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

# Push data to database
print("\nPushing data to Blazegraph...")
try:
    handler.pushDataToDb(csv_path)
    print("✓ Data pushed to database successfully!")
except ConnectionError as e:
    print(f"✗ Connection error (is Blazegraph running?): {e}")
except Exception as e:
    print(f"✗ Error pushing data: {e}")