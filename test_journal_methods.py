from QueryEngine import BasicQueryEngine
from impl import JournalQueryHandler
handler = JournalQueryHandler("data/doaj-csv.csv")

# ============================================
# URL Blazegraph
# ============================================
BLAZEGRAPH_URL = "http://172.20.10.2:9999/blazegraph/namespace/kb/sparql"  # endpoint

# ============================================
# TESTS
# ============================================

print("=" * 60)
print("TESTING BasicQueryEngine with Blazegraph")
print("=" * 60)

# creating engine and adding handler
engine = BasicQueryEngine()
handler = JournalQueryHandler(BLAZEGRAPH_URL)
engine.addJournalHandler(handler)

print(f"\n✓ Engine created")
print(f"✓ Handler connected to: {BLAZEGRAPH_URL}")

# --------------------------------------------
# Test 1: getAllJournals
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 1: getAllJournals()")
print("=" * 60)

try:
    journals = engine.getAllJournals()
    print(f"✓ Success! Found {len(journals)} journals")
    
    if journals:
        print(f"\nFirst journal details:")
        j = journals[0]
        print(f"  Title: {j.getTitle()}")
        print(f"  IDs: {j.getIds()}")
        print(f"  Languages: {j.getLanguage()}")
        print(f"  Publisher: {j.getPublisher()}")
        print(f"  Has DOAJ Seal: {j.hasDOAJSeal()}")
        print(f"  Has APC: {j.hasAPC()}")
        print(f"  License: {j.getLicense()}")
    else:
        print("⚠ Warning: No journals found in database")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 2: getJournalsWithTitle
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 2: getJournalsWithTitle('journal')")
print("=" * 60)

try:
    journals = engine.getJournalsWithTitle("journal")
    print(f"✓ Success! Found {len(journals)} journals with 'journal' in title")
    
    for i, j in enumerate(journals[:5], 1):  # первые 5
        print(f"  {i}. {j.getTitle()}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 3: getJournalsPublishedBy
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 3: getJournalsPublishedBy('springer')")
print("=" * 60)

try:
    journals = engine.getJournalsPublishedBy("springer")
    print(f"✓ Success! Found {len(journals)} journals by Springer")
    
    for i, j in enumerate(journals[:3], 1):  # первые 3
        print(f"  {i}. {j.getTitle()} - {j.getPublisher()}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 4: getJournalsWithLicense
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 4: getJournalsWithLicense({'CC BY'})")
print("=" * 60)

try:
    journals = engine.getJournalsWithLicense({"CC BY"})
    print(f"✓ Success! Found {len(journals)} journals with CC BY license")
    
    for i, j in enumerate(journals[:3], 1):
        print(f"  {i}. {j.getTitle()} - License: {j.getLicense()}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 5: getJournalsWithAPC
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 5: getJournalsWithAPC()")
print("=" * 60)

try:
    journals = engine.getJournalsWithAPC()
    print(f"✓ Success! Found {len(journals)} journals with APC")
    
    if journals:
        print(f"  Example: {journals[0].getTitle()} - APC: {journals[0].hasAPC()}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 6: getJournalsWithDOAJSeal
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 6: getJournalsWithDOAJSeal()")
print("=" * 60)

try:
    journals = engine.getJournalsWithDOAJSeal()
    print(f"✓ Success! Found {len(journals)} journals with DOAJ Seal")
    
    if journals:
        print(f"  Example: {journals[0].getTitle()} - Seal: {journals[0].hasDOAJSeal()}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 7: Check for duplicates
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 7: Checking for duplicates")
print("=" * 60)

try:
    journals = engine.getAllJournals()
    all_ids = []
    for j in journals:
        all_ids.extend(j.getIds())
    
    if len(all_ids) == len(set(all_ids)):
        print("✓ Success! No duplicate identifiers found")
    else:
        print(f"⚠ Warning: Found duplicates! Total IDs: {len(all_ids)}, Unique: {len(set(all_ids))}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# --------------------------------------------
# Test 8: Check data types
# --------------------------------------------
print("\n" + "=" * 60)
print("TEST 8: Checking data types")
print("=" * 60)

try:
    journals = engine.getAllJournals()
    if journals:
        j = journals[0]
        
        print(f"✓ Type of result: {type(journals)} - Expected: list")
        print(f"✓ Type of journal: {type(j)} - Expected: Journal")
        print(f"✓ Type of IDs: {type(j.getIds())} - Expected: list")
        print(f"✓ Type of languages: {type(j.getLanguage())} - Expected: list")
        print(f"✓ Type of seal: {type(j.hasDOAJSeal())} - Expected: bool")
        print(f"✓ Type of APC: {type(j.hasAPC())} - Expected: bool")
        
        # Check if values are correct
        assert isinstance(journals, list), "Result should be a list!"
        assert isinstance(j.getIds(), list), "IDs should be a list!"
        assert isinstance(j.hasDOAJSeal(), bool), "Seal should be boolean!"
        assert isinstance(j.hasAPC(), bool), "APC should be boolean!"
        
        print("\n✓ All type checks passed!")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)