import pandas as pd
from Handlers import JournalQueryHandler  # Check your actual filename!

# ================================
# CONFIG
# ================================
ENDPOINT = "http://10.44.28.33:9999/blazegraph/"  # Check this URL!
print("=" * 60)
print("Testing JournalQueryHandler")
print("Connecting to Blazegraph endpoint:")
print(ENDPOINT)
print("=" * 60)

qh = JournalQueryHandler(ENDPOINT)

# ================================
# 1. TEST: getAllJournals
# ================================
print("\n[TEST 1] getAllJournals()")
print("-" * 60)
df_all = qh.getAllJournals()
print(f"Total journals found: {len(df_all)}")
if not df_all.empty:
    print("\nFirst 3 journals:")
    print(df_all.head(3))
    print(f"\nColumns: {df_all.columns.tolist()}")
else:
    print("⚠️ WARNING: No journals found in database!")
assert isinstance(df_all, pd.DataFrame), "Should return DataFrame"

# ================================
# 2. TEST: getById (single ISSN/EISSN)
# ================================
print("\n[TEST 2] getById()")
print("-" * 60)
if not df_all.empty and '2075-2180' in df_all.columns:
    # Get first identifier (might be "1234-5678; 9876-5432" format)
    test_identifier = df_all.iloc[0]['2075-2180']
    # Extract first ISSN from combined string
    test_issn = test_identifier.split(';')[0].strip()
    print(f"Testing with ISSN: {test_issn}")
    
    df_one = qh.getById(test_issn)
    print(f"Results: {len(df_one)} journal(s)")
    if not df_one.empty:
        print(df_one)
    assert isinstance(df_one, pd.DataFrame), "Should return DataFrame"
else:
    print("⚠️ SKIP: No journals or identifier column found")

# ================================
# 3. TEST: getJournalsWithTitle
# ================================
print("\n[TEST 3] getJournalsWithTitle('Vestnik')")
print("-" * 60)
df_title = qh.getJournalsWithTitle("Vestnik")
print(f"Journals with 'Vestnik' in title: {len(df_title)}")
if not df_title.empty:
    print("\nFirst 3 results:")
    print(df_title[['title']].head(3) if 'title' in df_title.columns else df_title.head(3))
assert isinstance(df_title, pd.DataFrame), "Should return DataFrame"

# ================================
# 4. TEST: getJournalsPublishedBy
# ================================
print("\n[TEST 4] getJournalsPublishedBy('University')")
print("-" * 60)
df_pub = qh.getJournalsPublishedBy("University")
print(f"Journals published by 'University': {len(df_pub)}")
if not df_pub.empty:
    print("\nFirst 3 results:")
    print(df_pub[['title', 'publisher']].head(3) if 'title' in df_pub.columns else df_pub.head(3))
assert isinstance(df_pub, pd.DataFrame), "Should return DataFrame"

# ================================
# 5. TEST: getJournalsWithLicense
# ================================
print("\n[TEST 5] getJournalsWithLicense('CC BY')")
print("-" * 60)
df_license = qh.getJournalsWithLicense("CC BY")
print(f"Journals with 'CC BY' license: {len(df_license)}")
if not df_license.empty:
    print("\nFirst 3 results:")
    print(df_license[['title', 'license']].head(3) if 'title' in df_license.columns else df_license.head(3))
assert isinstance(df_license, pd.DataFrame), "Should return DataFrame"

# ================================
# 6. TEST: getJournalsWithAPC
# ================================
print("\n[TEST 6] getJournalsWithAPC()")
print("-" * 60)
df_apc = qh.getJournalsWithAPC()
print(f"Journals with APC: {len(df_apc)}")
if not df_apc.empty:
    print("\nFirst 3 results:")
    print(df_apc[['title', 'apc']].head(3) if 'title' in df_apc.columns else df_apc.head(3))
assert isinstance(df_apc, pd.DataFrame), "Should return DataFrame"

# ================================
# 7. TEST: getJournalsWithDOAJSeal
# ================================
print("\n[TEST 7] getJournalsWithDOAJSeal()")
print("-" * 60)
df_seal = qh.getJournalsWithDOAJSeal()
print(f"Journals with DOAJ Seal: {len(df_seal)}")
if not df_seal.empty:
    print("\nFirst 3 results:")
    print(df_seal[['title', 'seal']].head(3) if 'title' in df_seal.columns else df_seal.head(3))
assert isinstance(df_seal, pd.DataFrame), "Should return DataFrame"

# ================================
# 8. TEST: Empty input handling
# ================================
print("\n[TEST 8] Empty input handling")
print("-" * 60)
df_empty1 = qh.getById("")
df_empty2 = qh.getJournalsWithTitle("")
df_empty3 = qh.getJournalsPublishedBy("")
df_empty4 = qh.getJournalsWithLicense("")
print(f"getById(''): {len(df_empty1)} results (should be 0)")
print(f"getJournalsWithTitle(''): {len(df_empty2)} results (should be 0)")
assert df_empty1.empty and df_empty2.empty, "Empty inputs should return empty DataFrame"