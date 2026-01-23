import pandas as pd
from impl import JournalQueryHandler

# ================================
# CONFIG 
# ================================
ENDPOINT = "http://172.20.10.2:9999/blazegraph/namespace/kb/sparql" 
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
# 2. TEST: getById (Known IDs) 
# ================================
print("\n[TEST 2] getById() - Known Identifiers")
print("-" * 60)

test_ids = [
    "2238-8079",      
    "2075-2180",    
    "2788-4848",    
]

for test_id in test_ids:
    print(f"\n  Testing ID: '{test_id}'")
    df_result = qh.getById(test_id)
    
    if not df_result.empty:
        print(f"  ✅ Found {len(df_result)} journal(s)")
        print(f"     Title: {df_result.iloc[0].get('title', 'N/A')}")
        print(f"     Publisher: {df_result.iloc[0].get('publisher', 'N/A')}")
    else:
        print(f"  ⚠️ No journal found with this ID")
    
    assert isinstance(df_result, pd.DataFrame), "Should return DataFrame"
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
print("\n[TEST 4] getJournalsPublishedBy('Universidade')")
print("-" * 60)
df_pub = qh.getJournalsPublishedBy("Universidade")
print(f"Journals published by 'Universidade': {len(df_pub)}")
if not df_pub.empty:
    print("\nFirst 3 results:")
    print(df_pub[['title', 'publisher']].head(3) if 'title' in df_pub.columns else df_pub.head(3))
assert isinstance(df_pub, pd.DataFrame), "Should return DataFrame"

# ================================
# 5. TEST: getJournalsWithLicense
# ================================
print("\n[DEBUG] Getting all journals to see available licenses...")
df_all = qh.getAllJournals()
if not df_all.empty and 'license' in df_all.columns:
    unique_licenses = df_all['license'].dropna().unique()
    print(f"Found {len(unique_licenses)} unique licenses in database")
    print("\nFirst 10 licenses:")
    for i, lic in enumerate(list(unique_licenses)[:10], 1):
        print(f"  {i}. '{lic}'")
else:
    print("No licenses found or 'license' column missing")

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