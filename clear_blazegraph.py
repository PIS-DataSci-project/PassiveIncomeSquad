#!/usr/bin/env python3
"""Delete all data from Blazegraph triplestore"""

import requests

# Blazegraph endpoint
endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

print("=" * 60)
print("BLAZEGRAPH DATA DELETION")
print("=" * 60)
print(f"Endpoint: {endpoint}")
print()

# SPARQL UPDATE query to delete all triples
delete_query = """
DELETE WHERE {
  ?s ?p ?o .
}
"""

try:
    print("Sending DELETE request to Blazegraph...")
    
    # Send SPARQL UPDATE request
    response = requests.post(
        endpoint,
        data={"update": delete_query},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30
    )
    
    if response.status_code == 200:
        print("✓ All triples deleted successfully!")
        print()
        print("Blazegraph is now empty.")
    else:
        print(f"✗ Delete failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ Connection failed!")
    print()
    print("Make sure Blazegraph is running at:")
    print("  http://127.0.0.1:9999")
    
except Exception as e:
    print(f"✗ Error: {e}")

print("=" * 60)
