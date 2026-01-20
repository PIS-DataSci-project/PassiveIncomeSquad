import pandas as pd
from Handlers import JournalQueryHandler

# =====================================================
# CONFIG: Blazegraph endpoint
# =====================================================
ENDPOINT = "http://localhost:9999/blazegraph/namespace/doaj/sparql"

print("=" * 70)
print("TESTING JournalQueryHandler with Blazegraph")
print("Endpoint:", ENDPOINT)
print("=" * 70)

qh = JournalQueryHandler(ENDPOINT)

# =====================================================
# 1. getAllJournals
# =====================================================
print("\n[TEST 1] getAllJournals()")
df_all = qh.getAllJournals()

print("Rows:", len(df_all))
print(df_all.head())
assert isinstance(df_all, pd.DataFrame)

if df_all.empty:
    print("⚠️ No journals found — check TTL or prefixes")

# =====================================================
# 2. getById (ISSN or EISSN)
# =====================================================
print("\n[TEST 2] getById(ISSN/EISSN)")

if not df_all.empty:
    issn = df_all.iloc[0].get("issn")
    eissn = df_all.iloc[0].get("eissn")
    test_id = issn or eissn

    if test_id:
        print("Testing ID:", test_id)
        df_one = qh.getById(test_id)
        print(df_one)
        assert isinstance(df_one, pd.DataFrame)
    else:
        print("⚠️ No ISSN/EISSN found in first journal")
else:
    print("⚠️ Skipped (no journals)")

# =====================================================
# 3. getJournalsWithTitle
# =====================================================
print("\n[TEST 3] getJournalsWithTitle('medicine')")
df_title = qh.getJournalsWithTitle("medicine")
print("Rows:", len(df_title))
print(df_title.head())
assert isinstance(df_title, pd.DataFrame)

# =====================================================
# 4. getJournalsPublishedBy
# =====================================================
print("\n[TEST 4] getJournalsPublishedBy('university')")
df_pub = qh.getJournalsPublishedBy("university")
print("Rows:", len(df_pub))
print(df_pub.head())
assert isinstance(df_pub, pd.DataFrame)

# =====================================================
# 5. getJournalsWithLicense
# =====================================================
print("\n[TEST 5] getJournalsWithLicense({'CC BY'})")
df_lic = qh.getJournalsWithLicense({"CC BY"})
print("Rows:", len(df_lic))
print(df_lic.head())
assert isinstance(df_lic, pd.DataFrame)

# =====================================================
# 6. getJournalsWithAPC
# =====================================================
print("\n[TEST 6] getJournalsWithAPC()")
df_apc = qh.getJournalsWithAPC()
print("Rows:", len(df_apc))
print(df_apc.head())
assert isinstance(df_apc, pd.DataFrame)

# =====================================================
# 7. getJournalsWithDOAJSeal
# =====================================================
print("\n[TEST 7] getJournalsWithDOAJSeal()")
df_seal = qh.getJournalsWithDOAJSeal()
print("Rows:", len(df_seal))
print(df_seal.head())
assert isinstance(df_seal, pd.DataFrame)

print("\n" + "=" * 70)
print("✅ ALL JournalQueryHandler TESTS COMPLETED")
print("=" * 70)
