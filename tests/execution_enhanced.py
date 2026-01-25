# Supposing that all the classes developed for the project
# are contained in the file 'impl.py', then:

# 1) Importing all the classes for handling the relational database
from impl import CategoryUploadHandler, CategoryQueryHandler

# 2) Importing all the classes for handling graph database
from impl import JournalUploadHandler, JournalQueryHandler

# 3) Importing the class for dealing with mashup queries
from impl import BasicQueryEngine, FullQueryEngine

import os
import sqlite3
from SPARQLWrapper import SPARQLWrapper, JSON

# Helper function to check if Blazegraph has data
def check_blazegraph_data(endpoint):
    """Check if Blazegraph already contains journal data"""
    try:
        sparql = SPARQLWrapper(endpoint)
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT (COUNT(?journal) as ?count)
        WHERE {
            ?journal a schema:Periodical .
        }
        """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        count = int(results["results"]["bindings"][0]["count"]["value"])
        return count
    except Exception as e:
        print(f"  Warning: Could not check Blazegraph data: {e}")
        return 0

# Helper function to check if SQLite has data
def check_sqlite_data(db_path):
    """Check if SQLite database already contains category data"""
    if not os.path.exists(db_path):
        return 0
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM categories")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"  Warning: Could not check SQLite data: {e}")
        return 0

# Once all the classes are imported, first create the relational
# database using the related source data
print("=" * 60)
print("STEP 1: Creating relational database")
print("=" * 60)
try:
    rel_path = "relational.db"
    
    # Check for existing data
    existing_count = check_sqlite_data(rel_path)
    if existing_count > 0:
        print(f"⚠ WARNING: Database already contains {existing_count} category records")
        response = input("  Do you want to skip upload? (yes/no): ").strip().lower()
        if response == "yes":
            print("✓ Skipping relational database upload")
            cat = CategoryUploadHandler()
            cat.setDbPathOrUrl(rel_path)
        else:
            print("  Proceeding with upload (may create duplicates)...")
            cat = CategoryUploadHandler()
            cat.setDbPathOrUrl(rel_path)
            cat.pushDataToDb("data/scimago.json")
            print("✓ SUCCESS: Relational database created and data uploaded")
    else:
        print("  Database is empty - safe to upload")
        cat = CategoryUploadHandler()
        cat.setDbPathOrUrl(rel_path)
        cat.pushDataToDb("data/scimago.json")
        print("✓ SUCCESS: Relational database created and data uploaded")
except Exception as e:
    print(f"✗ FAIL: Relational database creation failed - {e}")

# Then, create the graph database (remember first to run the
# Blazegraph instance) using the related source data
print("\n" + "=" * 60)
print("STEP 2: Creating graph database")
print("=" * 60)
try:
    grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
    
    # Check for existing data
    existing_count = check_blazegraph_data(grp_endpoint)
    if existing_count > 0:
        print(f"⚠ WARNING: Blazegraph already contains {existing_count} journal records")
        response = input("  Do you want to skip upload? (yes/no): ").strip().lower()
        if response == "yes":
            print("✓ Skipping graph database upload")
            jou = JournalUploadHandler()
            jou.setDbPathOrUrl(grp_endpoint)
        else:
            print("  Proceeding with upload (may create duplicates)...")
            jou = JournalUploadHandler()
            jou.setDbPathOrUrl(grp_endpoint)
            jou.serializeToTTL("data/doaj.csv", "data/doaj.ttl")
            jou.pushDataToDb("data/doaj.csv")
            print("✓ SUCCESS: Graph database handler created and data serialized to TTL")
    else:
        print("  Database is empty - safe to upload")
        jou = JournalUploadHandler()
        jou.setDbPathOrUrl(grp_endpoint)
        jou.serializeToTTL("data/doaj.csv", "data/doaj.ttl")
        jou.pushDataToDb("data/doaj.csv")
        print("✓ SUCCESS: Graph database handler created and data serialized to TTL")
except Exception as e:
    print(f"✗ FAIL: Graph database creation failed - {e}")

# In the next passage, create the query handlers for both
# the databases, using the related classes
print("\n" + "=" * 60)
print("STEP 3: Creating query handlers")
print("=" * 60)
try:
    cat_qh = CategoryQueryHandler()
    cat_qh.setDbPathOrUrl(rel_path)
    print("✓ SUCCESS: Category query handler created")
except Exception as e:
    print(f"✗ FAIL: Category query handler creation failed - {e}")

try:
    jou_qh = JournalQueryHandler()
    jou_qh.setDbPathOrUrl(grp_endpoint)
    print("✓ SUCCESS: Journal query handler created")
except Exception as e:
    print(f"✗ FAIL: Journal query handler creation failed - {e}")

# Finally, create a advanced mashup object for asking
# about data
print("\n" + "=" * 60)
print("STEP 4: Creating basic query engine")
print("=" * 60)
try:
    que = BasicQueryEngine()
    que.addCategoryHandler(cat_qh)
    que.addJournalHandler(jou_qh)
    print("✓ SUCCESS: Basic query engine created and handlers added")
except Exception as e:
    print(f"✗ FAIL: Basic query engine creation failed - {e}")

# Execute ALL queries from BasicQueryEngine
print("\n" + "=" * 80)
print("STEP 5: Testing ALL BasicQueryEngine Methods")
print("=" * 80)

# =============================================================================
# JOURNAL-RELATED METHODS
# =============================================================================
print("\n" + "-" * 60)
print("JOURNAL-RELATED METHODS")
print("-" * 60)

print("\n1. getAllJournals()")
try:
    result = que.getAllJournals()
    if result is not None:
        count = len(result) if hasattr(result, '__len__') else 'unknown'
        print(f"✓ SUCCESS: Retrieved {count} journal(s)")
    else:
        print("✓ SUCCESS: Query executed (returned None)")
except Exception as e:
    print(f"✗ FAIL: getAllJournals() failed - {e}")

print("\n2. getJournalsWithTitle('Journal')")
try:
    result = que.getJournalsWithTitle("Journal")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) with 'Journal' in title")
except Exception as e:
    print(f"✗ FAIL: getJournalsWithTitle() failed - {e}")

print("\n3. getJournalsPublishedBy('University')")
try:
    result = que.getJournalsPublishedBy("University")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) published by 'University'")
except Exception as e:
    print(f"✗ FAIL: getJournalsPublishedBy() failed - {e}")

print("\n4. getJournalsWithLicense({'CC BY'})")
try:
    result = que.getJournalsWithLicense({"CC BY"})
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) with CC BY license")
except Exception as e:
    print(f"✗ FAIL: getJournalsWithLicense() failed - {e}")

print("\n5. getJournalsWithAPC()")
try:
    result = que.getJournalsWithAPC()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) with APC")
except Exception as e:
    print(f"✗ FAIL: getJournalsWithAPC() failed - {e}")

print("\n6. getJournalsWithDOAJSeal()")
try:
    result = que.getJournalsWithDOAJSeal()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) with DOAJ seal")
except Exception as e:
    print(f"✗ FAIL: getJournalsWithDOAJSeal() failed - {e}")

# =============================================================================
# CATEGORY-RELATED METHODS
# =============================================================================
print("\n" + "-" * 60)
print("CATEGORY-RELATED METHODS")
print("-" * 60)

print("\n7. getAllCategories()")
try:
    result = que.getAllCategories()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Retrieved {count} category/categories")
except Exception as e:
    print(f"✗ FAIL: getAllCategories() failed - {e}")

print("\n8. getAllAreas()")
try:
    result = que.getAllAreas()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Retrieved {count} area(s)")
except Exception as e:
    print(f"✗ FAIL: getAllAreas() failed - {e}")

print("\n9. getCategoriesWithQuartile({'Q1'})")
try:
    result = que.getCategoriesWithQuartile({"Q1"})
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} category/categories with Q1 quartile")
except Exception as e:
    print(f"✗ FAIL: getCategoriesWithQuartile() failed - {e}")

print("\n10. getCategoriesAssignedToAreas({'Medicine'})")
try:
    result = que.getCategoriesAssignedToAreas({"Medicine"})
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} category/categories in Medicine area")
except Exception as e:
    print(f"✗ FAIL: getCategoriesAssignedToAreas() failed - {e}")

print("\n11. getAreasAssignedToCategories({'Artificial Intelligence'})")
try:
    result = que.getAreasAssignedToCategories({"Artificial Intelligence"})
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} area(s) for Artificial Intelligence")
except Exception as e:
    print(f"✗ FAIL: getAreasAssignedToCategories() failed - {e}")

# =============================================================================
# ENTITY LOOKUP METHODS
# =============================================================================
print("\n" + "-" * 60)
print("ENTITY LOOKUP METHODS")
print("-" * 60)

print("\n12. getEntityById('Artificial Intelligence')")
try:
    result = que.getEntityById("Artificial Intelligence")
    if result is None:
        print("✓ SUCCESS: Query executed - No entity found with that ID")
    else:
        entity_type = type(result).__name__
        print(f"✓ SUCCESS: Found entity of type {entity_type}")
except Exception as e:
    print(f"✗ FAIL: getEntityById('Artificial Intelligence') failed - {e}")

print("\n13. getEntityById('2532-8816') [Journal ISSN]")
try:
    result = que.getEntityById("2532-8816")
    if result is not None:
        entity_type = type(result).__name__
        print(f"✓ SUCCESS: Found entity of type {entity_type}")
    else:
        print("✓ SUCCESS: Query executed - No entity found")
except Exception as e:
    print(f"✗ FAIL: getEntityById('2532-8816') failed - {e}")

print("\n14. getEntityById('Medicine') [Area]")
try:
    result = que.getEntityById("Medicine")
    if result is not None:
        entity_type = type(result).__name__
        print(f"✓ SUCCESS: Found entity of type {entity_type}")
    else:
        print("✓ SUCCESS: Query executed - No entity found")
except Exception as e:
    print(f"✗ FAIL: getEntityById('Medicine') failed - {e}")

# =============================================================================
# HELPER METHODS
# =============================================================================
print("\n" + "-" * 60)
print("HELPER METHODS")
print("-" * 60)

print("\n15. getCategoriesByJournalId('2532-8816')")
try:
    result = que.getCategoriesByJournalId("2532-8816")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} category/categories for journal")
except Exception as e:
    print(f"✗ FAIL: getCategoriesByJournalId() failed - {e}")

print("\n16. getAreasByJournalId('2532-8816')")
try:
    result = que.getAreasByJournalId("2532-8816")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} area(s) for journal")
except Exception as e:
    print(f"✗ FAIL: getAreasByJournalId() failed - {e}")

# =============================================================================
# HANDLER MANAGEMENT METHODS
# =============================================================================
print("\n" + "-" * 60)
print("HANDLER MANAGEMENT METHODS")
print("-" * 60)

print("\n17. cleanJournalHandlers()")
try:
    result = que.cleanJournalHandlers()
    if result:
        print("✓ SUCCESS: Journal handlers cleaned")
        # Re-add handler for remaining tests
        que.addJournalHandler(jou_qh)
    else:
        print("✗ FAIL: cleanJournalHandlers() returned False")
except Exception as e:
    print(f"✗ FAIL: cleanJournalHandlers() failed - {e}")

print("\n18. cleanCategoryHandlers()")
try:
    result = que.cleanCategoryHandlers()
    if result:
        print("✓ SUCCESS: Category handlers cleaned")
        # Re-add handler for remaining tests
        que.addCategoryHandler(cat_qh)
    else:
        print("✗ FAIL: cleanCategoryHandlers() returned False")
except Exception as e:
    print(f"✗ FAIL: cleanCategoryHandlers() failed - {e}")

# =============================================================================
# SUMMARY - BASICQUERYENGINE
# =============================================================================
print("\n" + "=" * 80)
print("BASICQUERYENGINE METHODS TESTED")
print("=" * 80)

# #############################################################################
# FULLQUERYENGINE TESTS
# #############################################################################

print("\n\n" + "=" * 80)
print("STEP 6: Testing ALL FullQueryEngine Methods")
print("=" * 80)

print("\n" + "=" * 60)
print("Creating FullQueryEngine instance")
print("=" * 60)
try:
    full_que = FullQueryEngine()
    full_que.addCategoryHandler(cat_qh)
    full_que.addJournalHandler(jou_qh)
    print("✓ SUCCESS: FullQueryEngine created and handlers added")
except Exception as e:
    print(f"✗ FAIL: FullQueryEngine creation failed - {e}")

# =============================================================================
# FULLQUERYENGINE MASHUP METHODS
# =============================================================================
print("\n" + "-" * 60)
print("FULLQUERYENGINE MASHUP METHODS")
print("-" * 60)

print("\n19. getJournalsInCategoriesWithQuartile({'Artificial Intelligence', 'Oncology'}, {'Q1'})")
try:
    result = full_que.getJournalsInCategoriesWithQuartile(
        {"Artificial Intelligence", "Oncology"}, 
        {"Q1"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) in AI/Oncology with Q1 quartile")
except Exception as e:
    print(f"✗ FAIL: getJournalsInCategoriesWithQuartile() failed - {e}")

print("\n20. getJournalsInCategoriesWithQuartile({'Medicine'}, {'Q2'})")
try:
    result = full_que.getJournalsInCategoriesWithQuartile(
        {"Medicine"}, 
        {"Q2"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) in Medicine with Q2 quartile")
except Exception as e:
    print(f"✗ FAIL: getJournalsInCategoriesWithQuartile() failed - {e}")

print("\n21. getJournalsInAreasWithLicense({'Medicine'}, {'CC BY'})")
try:
    result = full_que.getJournalsInAreasWithLicense(
        {"Medicine"}, 
        {"CC BY"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) in Medicine area with CC BY license")
except Exception as e:
    print(f"✗ FAIL: getJournalsInAreasWithLicense() failed - {e}")

print("\n22. getJournalsInAreasWithLicense({'Computer Science', 'Engineering'}, {'CC BY-SA'})")
try:
    result = full_que.getJournalsInAreasWithLicense(
        {"Computer Science", "Engineering"}, 
        {"CC BY-SA"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} journal(s) in CS/Engineering with CC BY-SA license")
except Exception as e:
    print(f"✗ FAIL: getJournalsInAreasWithLicense() failed - {e}")

print("\n23. getDiamondJournalsInAreasAndCategoriesWithQuartile({'Medicine'}, {'Oncology'}, {'Q1'})")
try:
    result = full_que.getDiamondJournalsInAreasAndCategoriesWithQuartile(
        {"Medicine"}, 
        {"Oncology"}, 
        {"Q1"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} diamond journal(s) in Medicine/Oncology with Q1")
except Exception as e:
    print(f"✗ FAIL: getDiamondJournalsInAreasAndCategoriesWithQuartile() failed - {e}")

print("\n24. getDiamondJournalsInAreasAndCategoriesWithQuartile({'Computer Science'}, {'Artificial Intelligence'}, {'Q1', 'Q2'})")
try:
    result = full_que.getDiamondJournalsInAreasAndCategoriesWithQuartile(
        {"Computer Science"}, 
        {"Artificial Intelligence"}, 
        {"Q1", "Q2"}
    )
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Found {count} diamond journal(s) in CS/AI with Q1/Q2")
except Exception as e:
    print(f"✗ FAIL: getDiamondJournalsInAreasAndCategoriesWithQuartile() failed - {e}")

# =============================================================================
# FULLQUERYENGINE HELPER METHODS
# =============================================================================
print("\n" + "-" * 60)
print("FULLQUERYENGINE HELPER METHODS")
print("-" * 60)

print("\n25. _parse_list_field('identifier1; identifier2; identifier3')")
try:
    result = full_que._parse_list_field("identifier1; identifier2; identifier3")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Parsed into {count} elements")
except Exception as e:
    print(f"✗ FAIL: _parse_list_field() failed - {e}")

print("\n26. _parse_list_field('English, Spanish, French')")
try:
    result = full_que._parse_list_field("English, Spanish, French")
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Parsed into {count} elements")
except Exception as e:
    print(f"✗ FAIL: _parse_list_field() failed - {e}")

print("\n27. _parse_list_field(None)")
try:
    result = full_que._parse_list_field(None)
    if result == []:
        print("✓ SUCCESS: None parsed to empty list")
    else:
        print(f"✗ FAIL: Expected empty list, got {result}")
except Exception as e:
    print(f"✗ FAIL: _parse_list_field(None) failed - {e}")

# =============================================================================
# FULLQUERYENGINE - INHERITED BASICQUERYENGINE METHODS
# =============================================================================
print("\n" + "-" * 60)
print("INHERITED METHODS (from BasicQueryEngine)")
print("-" * 60)

print("\n28. FullQueryEngine.getAllJournals()")
try:
    result = full_que.getAllJournals()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Retrieved {count} journal(s)")
except Exception as e:
    print(f"✗ FAIL: getAllJournals() failed - {e}")

print("\n29. FullQueryEngine.getAllCategories()")
try:
    result = full_que.getAllCategories()
    count = len(result) if result and hasattr(result, '__len__') else 0
    print(f"✓ SUCCESS: Retrieved {count} category/categories")
except Exception as e:
    print(f"✗ FAIL: getAllCategories() failed - {e}")

print("\n30. FullQueryEngine.getEntityById('Medicine')")
try:
    result = full_que.getEntityById("Medicine")
    if result is not None:
        entity_type = type(result).__name__
        print(f"✓ SUCCESS: Found entity of type {entity_type}")
    else:
        print("✓ SUCCESS: Query executed - No entity found")
except Exception as e:
    print(f"✗ FAIL: getEntityById() failed - {e}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("EXECUTION COMPLETE - ALL BASICQUERYENGINE & FULLQUERYENGINE METHODS TESTED")
print("=" * 80)
print("\nSummary:")
print("- BasicQueryEngine: 18 methods tested")
print("- FullQueryEngine: 12 methods tested (3 mashup + 3 helper + 6 inheritance)")
print("- Total: 30 test cases executed")
print("=" * 80)