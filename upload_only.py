"""
Comprehensive Query Execution Examples
Tests all methods in BasicQueryEngine with one example each
"""

from impl import JournalQueryHandler, CategoryQueryHandler, BasicQueryEngine

# ============================================
# CONFIGURATION
# ============================================
BLAZEGRAPH_URL = "http://127.0.0.1:9999/blazegraph/sparql"
RELATIONAL_DB = "relational.db"

# ============================================
# SETUP ENGINE AND HANDLERS
# ============================================
print("=" * 80)
print("BASICQUERYENGINE - COMPREHENSIVE QUERY EXECUTION EXAMPLES")
print("=" * 80)

engine = BasicQueryEngine()

# Add Journal Handler (Blazegraph)
journal_handler = JournalQueryHandler()
journal_handler.setDbPathOrUrl(BLAZEGRAPH_URL)
engine.addJournalHandler(journal_handler)

# Add Category Handler (SQLite)
category_handler = CategoryQueryHandler()
category_handler.setDbPathOrUrl(RELATIONAL_DB)
engine.addCategoryHandler(category_handler)

print(f"\n✓ Engine initialized")
print(f"✓ Journal Handler: {BLAZEGRAPH_URL}")
print(f"✓ Category Handler: {RELATIONAL_DB}")
print()

# ============================================
# HANDLER MANAGEMENT METHODS
# ============================================
print("=" * 80)
print("1. HANDLER MANAGEMENT METHODS")
print("=" * 80)

# Test: addJournalHandler (already done above)
print("\n[addJournalHandler]")
print(f"  ✓ Journal handlers count: {len(engine.journalQuery)}")

# Test: addCategoryHandler (already done above)
print("\n[addCategoryHandler]")
print(f"  ✓ Category handlers count: {len(engine.categoryQuery)}")

# Test: cleanJournalHandlers (demonstrate, then re-add)
print("\n[cleanJournalHandlers]")
original_count = len(engine.journalQuery)
engine.cleanJournalHandlers()
print(f"  ✓ Before clean: {original_count}, After clean: {len(engine.journalQuery)}")
# Re-add handler
engine.addJournalHandler(journal_handler)
print(f"  ✓ Re-added: {len(engine.journalQuery)}")

# Test: cleanCategoryHandlers (demonstrate, then re-add)
print("\n[cleanCategoryHandlers]")
original_count = len(engine.categoryQuery)
engine.cleanCategoryHandlers()
print(f"  ✓ Before clean: {original_count}, After clean: {len(engine.categoryQuery)}")
# Re-add handler
engine.addCategoryHandler(category_handler)
print(f"  ✓ Re-added: {len(engine.categoryQuery)}")

# ============================================
# JOURNAL-RELATED METHODS
# ============================================
print("\n" + "=" * 80)
print("2. JOURNAL-RELATED METHODS")
print("=" * 80)

# Test: getAllJournals
print("\n[getAllJournals]")
try:
    journals = engine.getAllJournals()
    print(f"  ✓ Found {len(journals)} journals")
    if journals:
        j = journals[0]
        print(f"  Example: '{j.getTitle()[:50]}...' (IDs: {j.getIds()[:2]})")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getJournalsWithTitle
print("\n[getJournalsWithTitle]")
try:
    journals = engine.getJournalsWithTitle("science")
    print(f"  ✓ Found {len(journals)} journals with 'science' in title")
    if journals:
        print(f"  Example: '{journals[0].getTitle()[:60]}...'")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getJournalsPublishedBy
print("\n[getJournalsPublishedBy]")
try:
    journals = engine.getJournalsPublishedBy("university")
    print(f"  ✓ Found {len(journals)} journals published by 'university'")
    if journals:
        print(f"  Example: '{journals[0].getTitle()[:50]}...' by {journals[0].getPublisher()[:40]}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getJournalsWithLicense
print("\n[getJournalsWithLicense]")
try:
    journals = engine.getJournalsWithLicense({"CC BY"})
    print(f"  ✓ Found {len(journals)} journals with 'CC BY' license")
    if journals:
        print(f"  Example: '{journals[0].getTitle()[:50]}...' - License: {journals[0].getLicense()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getJournalsWithAPC
print("\n[getJournalsWithAPC]")
try:
    journals = engine.getJournalsWithAPC()
    print(f"  ✓ Found {len(journals)} journals with APC")
    if journals:
        print(f"  Example: '{journals[0].getTitle()[:50]}...' - APC: {journals[0].hasAPC()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getJournalsWithDOAJSeal
print("\n[getJournalsWithDOAJSeal]")
try:
    journals = engine.getJournalsWithDOAJSeal()
    print(f"  ✓ Found {len(journals)} journals with DOAJ Seal")
    if journals:
        print(f"  Example: '{journals[0].getTitle()[:50]}...' - Seal: {journals[0].hasDOAJSeal()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ============================================
# CATEGORY-RELATED METHODS
# ============================================
print("\n" + "=" * 80)
print("3. CATEGORY-RELATED METHODS")
print("=" * 80)

# Test: getAllCategories
print("\n[getAllCategories]")
try:
    categories = engine.getAllCategories()
    print(f"  ✓ Found {len(categories)} categories")
    if categories:
        cat = categories[0]
        print(f"  Example: Category ID: {cat.getIds()[0]}, Quartile: {cat.getQuartile()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getAllAreas
print("\n[getAllAreas]")
try:
    areas = engine.getAllAreas()
    print(f"  ✓ Found {len(areas)} areas")
    if areas:
        print(f"  Example: {areas[0].getIds()[0]}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getCategoriesWithQuartile
print("\n[getCategoriesWithQuartile]")
try:
    categories = engine.getCategoriesWithQuartile({"Q1"})
    print(f"  ✓ Found {len(categories)} categories in Q1")
    if categories:
        cat = categories[0]
        print(f"  Example: Category ID: {cat.getIds()[0]}, Quartile: {cat.getQuartile()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getCategoriesAssignedToAreas
print("\n[getCategoriesAssignedToAreas]")
try:
    categories = engine.getCategoriesAssignedToAreas({"Computer Science"})
    print(f"  ✓ Found {len(categories)} categories in 'Computer Science' area")
    if categories:
        cat = categories[0]
        print(f"  Example: Category ID: {cat.getIds()[0]}, Quartile: {cat.getQuartile()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getAreasAssignedToCategories
print("\n[getAreasAssignedToCategories]")
try:
    # First get a category ID to use
    all_cats = engine.getAllCategories()
    if all_cats:
        test_cat_id = all_cats[0].getIds()[0]
        areas = engine.getAreasAssignedToCategories({test_cat_id})
        print(f"  ✓ Found {len(areas)} areas for category '{test_cat_id}'")
        if areas:
            print(f"  Example: {areas[0].getIds()[0]}")
    else:
        print(f"  ⚠ No categories available for testing")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ============================================
# GET ENTITIES BY ID METHODS
# ============================================
print("\n" + "=" * 80)
print("4. GET ENTITIES BY ID METHODS")
print("=" * 80)

# Test: getCategoriesByJournalId
print("\n[getCategoriesByJournalId]")
try:
    # Get a journal ID first
    journals = engine.getAllJournals()
    if journals:
        test_journal_id = journals[0].getIds()[0]
        categories = engine.getCategoriesByJournalId(test_journal_id)
        print(f"  ✓ Found {len(categories)} categories for journal ID '{test_journal_id}'")
        if categories:
            print(f"  Example: Category ID: {categories[0].getIds()[0]}, Quartile: {categories[0].getQuartile()}")
        else:
            print(f"  Note: No categories associated with this journal")
    else:
        print(f"  ⚠ No journals available for testing")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getAreasByJournalId
print("\n[getAreasByJournalId]")
try:
    # Get a journal ID first
    journals = engine.getAllJournals()
    if journals:
        test_journal_id = journals[0].getIds()[0]
        areas = engine.getAreasByJournalId(test_journal_id)
        print(f"  ✓ Found {len(areas)} areas for journal ID '{test_journal_id}'")
        if areas:
            print(f"  Example: {areas[0].getIds()[0]}")
        else:
            print(f"  Note: No areas associated with this journal")
    else:
        print(f"  ⚠ No journals available for testing")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getEntityById (Journal)
print("\n[getEntityById - Journal]")
try:
    journals = engine.getAllJournals()
    if journals:
        test_id = journals[0].getIds()[0]
        entity = engine.getEntityById(test_id)
        if entity:
            print(f"  ✓ Found entity with ID '{test_id}'")
            print(f"  Type: {type(entity).__name__}")
            print(f"  Title: '{entity.getTitle()[:50]}...'")
            print(f"  Categories: {len(entity.getCategories())}, Areas: {len(entity.getAreas())}")
        else:
            print(f"  ✗ Entity not found")
    else:
        print(f"  ⚠ No journals available for testing")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getEntityById (Category)
print("\n[getEntityById - Category]")
try:
    categories = engine.getAllCategories()
    if categories:
        test_id = categories[0].getIds()[0]
        entity = engine.getEntityById(test_id)
        if entity:
            print(f"  ✓ Found entity with ID '{test_id}'")
            print(f"  Type: {type(entity).__name__}")
            print(f"  Quartile: {entity.getQuartile()}")
        else:
            print(f"  ✗ Entity not found")
    else:
        print(f"  ⚠ No categories available for testing")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test: getEntityById (Non-existent)
print("\n[getEntityById - Non-existent]")
try:
    entity = engine.getEntityById("NONEXISTENT-ID-12345")
    if entity is None:
        print(f"  ✓ Correctly returned None for non-existent ID")
    else:
        print(f"  ✗ Unexpected result: found entity")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 80)
print("EXECUTION COMPLETE")
print("=" * 80)
print("\nAll methods have been executed with example queries.")
print("Check the output above for results from each method.")
print()
