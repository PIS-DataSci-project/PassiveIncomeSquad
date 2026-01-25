# Test script - save as test_fixes.py
from impl import BasicQueryEngine, JournalQueryHandler, CategoryQueryHandler

print("=" * 60)
print("TESTING IMMEDIATE FIXES")
print("=" * 60)

# Test 1: Check imports
print("\n1. Testing imports...")
try:
    from pandas import read_csv
    print("✓ read_csv import works")
except ImportError as e:
    print(f"✗ Import failed: {e}")

# Test 2: Check methods exist
print("\n2. Testing BasicQueryEngine methods...")
engine = BasicQueryEngine()

if hasattr(engine, 'getCategoriesByJournalId'):
    print("✓ getCategoriesByJournalId exists")
else:
    print("✗ getCategoriesByJournalId MISSING")

if hasattr(engine, 'getAreasByJournalId'):
    print("✓ getAreasByJournalId exists")
else:
    print("✗ getAreasByJournalId MISSING")

# Test 3: Setup and test
print("\n3. Testing full integration...")
jq = JournalQueryHandler()
jq.setDbPathOrUrl("http://127.0.0.1:8080/blazegraph/sparql")
engine.addJournalHandler(jq)

cq = CategoryQueryHandler()
cq.setDbPathOrUrl("relational.db")
engine.addCategoryHandler(cq)

# Test getCategoriesByJournalId
print("\n4. Testing getCategoriesByJournalId...")
try:
    categories = engine.getCategoriesByJournalId("2532-8816")
    print(f"✓ Method works, returned: {categories}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test getAreasByJournalId
print("\n5. Testing getAreasByJournalId...")
try:
    areas = engine.getAreasByJournalId("2532-8816")
    print(f"✓ Method works, returned: {areas}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test getEntityById
print("\n6. Testing getEntityById...")
try:
    entity = engine.getEntityById("2532-8816")
    if entity:
        print(f"✓ Found entity: {type(entity).__name__}")
        print(f"  Title: {entity.getTitle() if hasattr(entity, 'getTitle') else 'N/A'}")
        print(f"  Categories: {entity.getCategories() if hasattr(entity, 'getCategories') else 'N/A'}")
        print(f"  Areas: {entity.getAreas() if hasattr(entity, 'getAreas') else 'N/A'}")
    else:
        print("✗ Entity not found")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)