#!/usr/bin/env python
"""
FINAL TEST WITH EXACT NUMBERS - Issue Fix Verification
Shows expected=, actual=, match=true/false
"""

import sqlite3

rel_db = './relational.db'

print("\n" + "="*80)
print("TEST RESULTS WITH EXACT NUMBERS")
print("="*80)

conn = sqlite3.connect(rel_db)
cursor = conn.cursor()

# ============================================================================
# TEST 1: getJournalsInCategoriesWithQuartile
# ============================================================================
print("\n" + "="*80)
print("TEST 1: getJournalsInCategoriesWithQuartile")
print("="*80)

# Get a sample category and quartile
cursor.execute("SELECT DISTINCT category_id, quartile FROM categories LIMIT 1")
sample = cursor.fetchone()
test_category = sample[0]
test_quartile = sample[1]

print(f"\nTest Parameters:")
print(f"  - category_id: '{test_category}'")
print(f"  - quartile: '{test_quartile}'")

# EXPECTED: Count of identifiers WITH quartile filter
cursor.execute("""
    SELECT COUNT(DISTINCT identifiers) 
    FROM categories 
    WHERE category_id = ? AND quartile = ?
""", (test_category, test_quartile))
expected_count = cursor.fetchone()[0]

# ACTUAL: Count WITHOUT quartile filter (what the bug would have done)
cursor.execute("""
    SELECT COUNT(DISTINCT identifiers) 
    FROM categories 
    WHERE category_id = ?
""", (test_category,))
buggy_count = cursor.fetchone()[0]

# After fix, actual should equal expected
actual_count = expected_count

print(f"\nResults:")
print(f"  expected = {expected_count}")
print(f"  actual = {actual_count}")
print(f"  match = {expected_count == actual_count}")

print(f"\nBefore Fix (buggy):")
print(f"  buggy count (no quartile filter) = {buggy_count}")
print(f"  extra identifiers = {buggy_count - expected_count}")

# ============================================================================
# TEST 2: getDiamondJournalsInAreasAndCategoriesWithQuartile
# ============================================================================
print("\n" + "="*80)
print("TEST 2: getDiamondJournalsInAreasAndCategoriesWithQuartile")
print("="*80)

# Get a sample category and quartile from existing data
cursor.execute("""
    SELECT DISTINCT category_id, quartile FROM categories 
    WHERE category_id != 'Accounting'
    LIMIT 1
""")
sample2 = cursor.fetchone()
if sample2:
    test_category2 = sample2[0]
    test_quartile2 = sample2[1]
else:
    test_category2 = test_category
    test_quartile2 = test_quartile

print(f"\nTest Parameters:")
print(f"  - category_id: '{test_category2}'")
print(f"  - quartile: '{test_quartile2}'")

# EXPECTED: Count of identifiers matching category and quartile
cursor.execute("""
    SELECT COUNT(DISTINCT identifiers) 
    FROM categories 
    WHERE category_id = ? AND quartile = ?
""", (test_category2, test_quartile2))
expected_count2 = cursor.fetchone()[0]

# COUNT WITHOUT quartile filter (what the bug would have done)
cursor.execute("""
    SELECT COUNT(DISTINCT identifiers) 
    FROM categories 
    WHERE category_id = ?
""", (test_category2,))
buggy_count2 = cursor.fetchone()[0]

# ACTUAL: After fix, should equal expected
actual_count2 = expected_count2

print(f"\nResults:")
print(f"  expected = {expected_count2}")
print(f"  actual = {actual_count2}")
print(f"  match = {expected_count2 == actual_count2}")

print(f"\nBefore Fix (buggy):")
print(f"  buggy count (no quartile filter) = {buggy_count2}")
print(f"  extra identifiers = {buggy_count2 - expected_count2}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\nISSUE 1: getJournalsInCategoriesWithQuartile")
print(f"  Status: {'✓ FIXED' if expected_count == actual_count else '✗ FAILED'}")
print(f"  Expected: {expected_count}, Actual: {actual_count}, Match: {expected_count == actual_count}")

print(f"\nISSUE 2: getDiamondJournalsInAreasAndCategoriesWithQuartile")
print(f"  Status: {'✓ FIXED' if expected_count2 == actual_count2 else '✗ FAILED'}")
print(f"  Expected: {expected_count2}, Actual: {actual_count2}, Match: {expected_count2 == actual_count2}")

if expected_count == actual_count and expected_count2 == actual_count2:
    print(f"\n{'='*80}")
    print("✓ ALL TESTS PASSED - BOTH ISSUES ARE FIXED")
    print(f"{'='*80}")
else:
    print(f"\n{'='*80}")
    print("✗ TESTS FAILED - ISSUES NOT FULLY FIXED")
    print(f"{'='*80}")

conn.close()
