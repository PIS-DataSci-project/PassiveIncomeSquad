"""
Test script for getEntityById method - Claudia
"""
import sys
sys.path.insert(0, 'do_methods_here!')

from impl import *
from QueryEngine import BasicQueryEngine

# Database paths - adjust if needed
GRAPH_DB = "http://127.0.0.1:9999/blazegraph/sparql"
RELATIONAL_DB = "./relational.db"

def test_getEntityById():
    """Test the getEntityById method"""
    
    print("=" * 60)
    print("Testing getEntityById Method")
    print("=" * 60)
    
    # Create query engine
    engine = BasicQueryEngine()
    
    # Set up journal query handler (graph database)
    journal_handler = JournalQueryHandler()
    journal_handler.setDbPathOrUrl(GRAPH_DB)
    engine.addJournalHandler(journal_handler)
    
    # Set up category query handler (relational database)
    category_handler = CategoryQueryHandler()
    category_handler.setDbPathOrUrl(RELATIONAL_DB)
    engine.addCategoryHandler(category_handler)
    
    print("\n✓ Query handlers set up successfully\n")
    
    # Test 1: Search for a journal by ISSN
    print("-" * 60)
    print("Test 1: Search for Journal by ISSN")
    print("-" * 60)
    journal_id = "2073-4859"  # Replace with an actual ISSN from your data
    result = engine.getEntityById(journal_id)
    
    if result:
        print(f"✓ Found entity: {type(result).__name__}")
        if isinstance(result, Journal):
            print(f"  - IDs: {result.getIds()}")
            print(f"  - Title: {result.getTitle()}")
            print(f"  - Publisher: {result.getPublisher()}")
            print(f"  - Language: {result.getLanguage()}")
            print(f"  - DOAJ Seal: {result.hasDOAJSeal()}")
            print(f"  - APC: {result.hasAPC()}")
    else:
        print(f"✗ No entity found with ID: {journal_id}")
    
    # Test 2: Search for a category
    print("\n" + "-" * 60)
    print("Test 2: Search for Category")
    print("-" * 60)
    category_id = "1234"  # Replace with an actual category ID from your data
    result = engine.getEntityById(category_id)
    
    if result:
        print(f"✓ Found entity: {type(result).__name__}")
        if isinstance(result, Category):
            print(f"  - IDs: {result.getIds()}")
            print(f"  - Quartile: {result.getQuartile()}")
    else:
        print(f"✗ No entity found with ID: {category_id}")
    
    # Test 3: Search for a non-existent ID
    print("\n" + "-" * 60)
    print("Test 3: Search for Non-existent ID")
    print("-" * 60)
    fake_id = "FAKE-ID-12345"
    result = engine.getEntityById(fake_id)
    
    if result is None:
        print(f"✓ Correctly returned None for non-existent ID: {fake_id}")
    else:
        print(f"✗ Unexpected result: {result}")
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_getEntityById()
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
