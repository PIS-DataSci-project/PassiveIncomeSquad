# test_queryengine_simple.py
# Testing BasicQueryEngine (assumes databases already populated)

from impl import CategoryQueryHandler, JournalQueryHandler, BasicQueryEngine

print("=" * 70)
print("TESTING BasicQueryEngine with impl_backup.py")
print("=" * 70)

# Database paths (assuming already populated)
rel_path = "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

# Create query handlers
print("\n[1] Creating query handlers...")
cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(rel_path)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)
print("✓ Query handlers created")

# Create query engine
print("\n[2] Creating BasicQueryEngine...")
que = BasicQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)
print("✓ QueryEngine ready")

print("\n" + "=" * 70)
print("RUNNING TESTS")
print("=" * 70)

# Track errors
error_count = 0
total_tests = 10

# Test 1: Get all journals
print("\n[TEST 1] getAllJournals()")
print("-" * 70)
try:
    result_q1 = que.getAllJournals()
    print(f"✓ Found {len(result_q1)} journals")
    if result_q1:
        print(f"  Sample: {result_q1[0].getTitle()}")
        print(f"  IDs: {result_q1[0].getIds()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 2: Get entity by category ID
print("\n[TEST 2] getEntityById('Artificial Intelligence')")
print("-" * 70)
try:
    result_q3 = que.getEntityById("Artificial Intelligence")
    if result_q3:
        print(f"✓ Found entity: {type(result_q3).__name__}")
        print(f"  IDs: {result_q3.getIds()}")
        if hasattr(result_q3, 'getQuartile'):
            print(f"  Quartile: {result_q3.getQuartile()}")
    else:
        print("✗ Entity not found (returned None)")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 3: Get entity by journal ISSN
print("\n[TEST 3] getEntityById('2096-6652')")
print("-" * 70)
try:
    result_q4 = que.getEntityById("2096-6652")
    if result_q4:
        print(f"✓ Found entity: {type(result_q4).__name__}")
        print(f"  IDs: {result_q4.getIds()}")
        if hasattr(result_q4, 'getTitle'):
            print(f"  Title: {result_q4.getTitle()}")
            print(f"  Publisher: {result_q4.getPublisher()}")
            print(f"  Has DOAJ Seal: {result_q4.hasDOAJSeal()}")
            print(f"  Has APC: {result_q4.hasAPC()}")
            print(f"  Categories: {len(result_q4.getCategories())}")
            print(f"  Areas: {len(result_q4.getAreas())}")
    else:
        print("✗ Entity not found (returned None)")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 4: Get all categories
print("\n[TEST 4] getAllCategories()")
print("-" * 70)
try:
    all_categories = que.getAllCategories()
    print(f"✓ Found {len(all_categories)} categories")
    if all_categories:
        print(f"  Sample: {all_categories[0].getIds()[0]}")
        print(f"  Quartile: {all_categories[0].getQuartile()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 5: Get all areas
print("\n[TEST 5] getAllAreas()")
print("-" * 70)
try:
    all_areas = que.getAllAreas()
    print(f"✓ Found {len(all_areas)} areas")
    if all_areas:
        print(f"  Sample areas: {[area.getIds()[0] for area in all_areas[:5]]}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 6: Get journals with title
print("\n[TEST 6] getJournalsWithTitle('Journal')")
print("-" * 70)
try:
    journals_with_title = que.getJournalsWithTitle("Journal")
    print(f"✓ Found {len(journals_with_title)} journals containing 'Journal'")
    if journals_with_title:
        print(f"  Sample: {journals_with_title[0].getTitle()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 7: Get journals with DOAJ Seal
print("\n[TEST 7] getJournalsWithDOAJSeal()")
print("-" * 70)
try:
    seal_journals = que.getJournalsWithDOAJSeal()
    print(f"✓ Found {len(seal_journals)} journals with DOAJ Seal")
    if seal_journals:
        print(f"  Sample: {seal_journals[0].getTitle()}")
        print(f"  Has Seal: {seal_journals[0].hasDOAJSeal()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 8: Get journals with APC
print("\n[TEST 8] getJournalsWithAPC()")
print("-" * 70)
try:
    apc_journals = que.getJournalsWithAPC()
    print(f"✓ Found {len(apc_journals)} journals with APC")
    if apc_journals:
        print(f"  Sample: {apc_journals[0].getTitle()}")
        print(f"  Has APC: {apc_journals[0].hasAPC()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 9: Get categories with quartile
print("\n[TEST 9] getCategoriesWithQuartile({'Q1'})")
print("-" * 70)
try:
    q1_categories = que.getCategoriesWithQuartile({"Q1"})
    print(f"✓ Found {len(q1_categories)} Q1 categories")
    if q1_categories:
        print(f"  Sample: {q1_categories[0].getIds()[0]}")
        print(f"  Quartile: {q1_categories[0].getQuartile()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

# Test 10: Get journals published by specific publisher
print("\n[TEST 10] getJournalsPublishedBy('University')")
print("-" * 70)
try:
    uni_journals = que.getJournalsPublishedBy("University")
    print(f"✓ Found {len(uni_journals)} journals published by entities with 'University'")
    if uni_journals:
        print(f"  Sample: {uni_journals[0].getTitle()}")
        print(f"  Publisher: {uni_journals[0].getPublisher()}")
except Exception as e:
    print(f"✗ Error: {e}")
    error_count += 1

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if error_count > 0:
    print(f"⚠️  THERE ARE ERRORS: {error_count}/{total_tests} tests failed")
else:
    print("✅ EXECUTION SUCCESSFUL: All tests passed without errors")

print("=" * 70)