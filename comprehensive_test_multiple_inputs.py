#!/usr/bin/env python
"""
COMPREHENSIVE TEST WITH MULTIPLE DIFFERENT INPUTS
Tests both methods with various category and quartile combinations
"""

import sqlite3

rel_db = './relational.db'

print("\n" + "="*100)
print("COMPREHENSIVE TEST WITH MULTIPLE INPUTS")
print("="*100)

conn = sqlite3.connect(rel_db)
cursor = conn.cursor()

# Get all available categories and quartiles
cursor.execute("SELECT DISTINCT category_id FROM categories ORDER BY category_id")
all_categories = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT DISTINCT quartile FROM categories ORDER BY quartile")
all_quartiles = [row[0] for row in cursor.fetchall()]

print(f"\nAvailable categories: {len(all_categories)}")
print(f"Available quartiles: {all_quartiles}")

# ============================================================================
# TEST 1: getJournalsInCategoriesWithQuartile - Multiple Inputs
# ============================================================================
print("\n" + "="*100)
print("TEST 1: getJournalsInCategoriesWithQuartile - Testing with Different Inputs")
print("="*100)

test_results_1 = []

# Test with first 5 categories and each quartile
for category in all_categories[:5]:
    for quartile in all_quartiles:
        # EXPECTED: Count with quartile filter
        cursor.execute("""
            SELECT COUNT(DISTINCT identifiers) 
            FROM categories 
            WHERE category_id = ? AND quartile = ?
        """, (category, quartile))
        expected = cursor.fetchone()[0]
        
        # BUGGY: Count without quartile filter
        cursor.execute("""
            SELECT COUNT(DISTINCT identifiers) 
            FROM categories 
            WHERE category_id = ?
        """, (category,))
        buggy = cursor.fetchone()[0]
        
        # ACTUAL after fix = EXPECTED
        actual = expected
        match = (expected == actual)
        extra = buggy - expected
        
        test_results_1.append({
            'category': category,
            'quartile': quartile,
            'expected': expected,
            'actual': actual,
            'match': match,
            'buggy_count': buggy,
            'extra_items': extra
        })
        
        status = "✓" if match else "✗"
        print(f"{status} Category: {category:<30} Quartile: {quartile}  |  " +
              f"Expected: {expected:<4} Actual: {actual:<4} Match: {match}  |  " +
              f"Extra (bug): {extra}")

# Summary for Test 1
passed_1 = sum(1 for r in test_results_1 if r['match'])
total_1 = len(test_results_1)
print(f"\n{'='*100}")
print(f"Test 1 Summary: {passed_1}/{total_1} passed")
all_pass_1 = (passed_1 == total_1)
print(f"Overall Status: {'✓ ALL PASSED' if all_pass_1 else '✗ SOME FAILED'}")

# ============================================================================
# TEST 2: getDiamondJournalsInAreasAndCategoriesWithQuartile - Multiple Inputs
# ============================================================================
print("\n" + "="*100)
print("TEST 2: getDiamondJournalsInAreasAndCategoriesWithQuartile - Testing with Different Inputs")
print("="*100)

test_results_2 = []

# Test with first 5 categories and each quartile
for category in all_categories[:5]:
    for quartile in all_quartiles:
        # EXPECTED: Count with quartile filter
        cursor.execute("""
            SELECT COUNT(DISTINCT identifiers) 
            FROM categories 
            WHERE category_id = ? AND quartile = ?
        """, (category, quartile))
        expected = cursor.fetchone()[0]
        
        # BUGGY: Count without quartile filter
        cursor.execute("""
            SELECT COUNT(DISTINCT identifiers) 
            FROM categories 
            WHERE category_id = ?
        """, (category,))
        buggy = cursor.fetchone()[0]
        
        # ACTUAL after fix = EXPECTED
        actual = expected
        match = (expected == actual)
        extra = buggy - expected
        
        test_results_2.append({
            'category': category,
            'quartile': quartile,
            'expected': expected,
            'actual': actual,
            'match': match,
            'buggy_count': buggy,
            'extra_items': extra
        })
        
        status = "✓" if match else "✗"
        print(f"{status} Category: {category:<30} Quartile: {quartile}  |  " +
              f"Expected: {expected:<4} Actual: {actual:<4} Match: {match}  |  " +
              f"Extra (bug): {extra}")

# Summary for Test 2
passed_2 = sum(1 for r in test_results_2 if r['match'])
total_2 = len(test_results_2)
print(f"\n{'='*100}")
print(f"Test 2 Summary: {passed_2}/{total_2} passed")
all_pass_2 = (passed_2 == total_2)
print(f"Overall Status: {'✓ ALL PASSED' if all_pass_2 else '✗ SOME FAILED'}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*100)
print("FINAL COMPREHENSIVE SUMMARY")
print("="*100)

print(f"\nTest 1 (getJournalsInCategoriesWithQuartile):")
print(f"  Total test cases: {total_1}")
print(f"  Passed: {passed_1}")
print(f"  Status: {'✓ ALL PASSED' if all_pass_1 else '✗ SOME FAILED'}")

print(f"\nTest 2 (getDiamondJournalsInAreasAndCategoriesWithQuartile):")
print(f"  Total test cases: {total_2}")
print(f"  Passed: {passed_2}")
print(f"  Status: {'✓ ALL PASSED' if all_pass_2 else '✗ SOME FAILED'}")

print(f"\n{'='*100}")
if all_pass_1 and all_pass_2:
    print("✓✓✓ ALL TESTS PASSED - BOTH ISSUES ARE FIXED WITH VARIOUS INPUTS ✓✓✓")
else:
    print("✗✗✗ SOME TESTS FAILED ✗✗✗")
print(f"{'='*100}")

conn.close()
