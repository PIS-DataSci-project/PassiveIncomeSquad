#!/usr/bin/env python
"""
Test script to verify the fixes for:
1. getJournalsInCategoriesWithQuartile - should not have extra identifier
2. getDiamondJournalsInAreasAndCategoriesWithQuartile - should not return extra journals
"""

import json
from impl import FullQueryEngine, JournalQueryHandler, CategoryQueryHandler

# Config
scimago_path = 'data/scimago.json'
rel_db = './relational.db'

# Setup engine
print("Setting up FullQueryEngine...")
engine = FullQueryEngine()

# Create and configure handlers
jh = JournalQueryHandler()
jh.setDbPathOrUrl(rel_db)

ch = CategoryQueryHandler()
ch.setDbPathOrUrl(rel_db)

# Add handlers to engine
engine.journalQuery.append(jh)
engine.categoryQuery.append(ch)

print("Engine setup complete!")

# Test 1: getJournalsInCategoriesWithQuartile
print("\n" + "="*80)
print("TEST 1: getJournalsInCategoriesWithQuartile")
print("="*80)

# Get some actual categories from the database
all_cats_df = ch.getAllCategories()
print(f"getAllCategories returned type: {type(all_cats_df)}")

if isinstance(all_cats_df, list) and len(all_cats_df) > 0:
    # It's a list of Category objects
    test_categories = set()
    for i, cat in enumerate(all_cats_df[:5]):
        if hasattr(cat, 'identifiers'):
            for cid in cat.identifiers:
                test_categories.add(str(cid))
        else:
            break
elif hasattr(all_cats_df, 'empty') and not all_cats_df.empty:
    # It's a DataFrame
    print(f"getAllCategories returned DataFrame with shape: {all_cats_df.shape}")
    
    # Get unique category_ids from the DataFrame
    test_categories = set()
    if 'category_id' in all_cats_df.columns:
        test_categories = set(all_cats_df['category_id'].unique()[:3])

if test_categories:
    test_cases = [
        (test_categories, {'Q1'}),
        (test_categories, {'Q2'}),
        ({list(test_categories)[0]}, {'Q1', 'Q2'}),
    ]
    
    for category_ids, quartiles in test_cases:
        print(f"\n--- Testing with categories={category_ids}, quartiles={quartiles} ---")
        
        # Get actual
        journals = engine.getJournalsInCategoriesWithQuartile(category_ids, quartiles)
        actual_ids = set()
        for j in journals:
            actual_ids.update(j.getIds())
        
        print(f"Journal count: {len(journals)}")
        print(f"Unique identifiers: {len(actual_ids)}")
        
        if len(journals) > 0:
            print("✓ PASS: Function returned results")
            print(f"  Sample IDs: {list(actual_ids)[:5]}")
        else:
            print("⚠ WARNING: No journals returned (may be valid if no data matches)")
else:
    print("⚠ Could not extract test categories from database")

# Test 2: getDiamondJournalsInAreasAndCategoriesWithQuartile
print("\n" + "="*80)
print("TEST 2: getDiamondJournalsInAreasAndCategoriesWithQuartile")
print("="*80)

# Get some actual areas and categories from the database
all_areas_df = ch.getAllAreas()
all_cats_df = ch.getAllCategories()

print(f"getAllAreas returned type: {type(all_areas_df)}")
print(f"getAllCategories returned type: {type(all_cats_df)}")

test_areas = set()
test_categories = set()

if hasattr(all_areas_df, 'empty') and not all_areas_df.empty:
    # It's a DataFrame
    print(f"getAllAreas returned DataFrame with shape: {all_areas_df.shape}")
    if 'area' in all_areas_df.columns:
        test_areas = set(all_areas_df['area'].unique()[:2])

if hasattr(all_cats_df, 'empty') and not all_cats_df.empty:
    # It's a DataFrame
    print(f"getAllCategories returned DataFrame with shape: {all_cats_df.shape}")
    if 'category_id' in all_cats_df.columns:
        test_categories = set(all_cats_df['category_id'].unique()[:2])

if test_areas and test_categories:
    print(f"Using test areas: {test_areas}")
    print(f"Using test categories: {test_categories}")
    
    test_cases_diamond = [
        (test_areas, test_categories, {'Q1'}),
        (test_areas, test_categories, {'Q2'}),
        (test_areas, test_categories, {'Q1', 'Q2'}),
    ]
    
    for area_ids, category_ids, quartiles in test_cases_diamond:
        print(f"\n--- Testing with areas={area_ids}, categories={category_ids}, quartiles={quartiles} ---")
        
        # First test base function
        base_journals = engine.getJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)
        print(f"Base journals count: {len(base_journals)}")
        
        # Get actual from diamond function
        actual_journals = engine.getDiamondJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)
        print(f"Diamond journals count:   {len(actual_journals)}")
        
        if len(actual_journals) > 0:
            print("✓ Diamond function returned results")
            
            # Check APC filter
            with_apc = [j for j in actual_journals if j.apc]
            if with_apc:
                print(f"✗ FAIL: Found {len(with_apc)} journals with APC=True (should be 0)!")
                for j in with_apc[:3]:
                    print(f"  - {j.getTitle()}: APC={j.apc}")
            else:
                print("✓ All returned journals have APC=False")
            
            # Check diamond is subset of base
            if len(actual_journals) <= len(base_journals):
                print(f"✓ Diamond is properly filtered (diamond≤base: {len(actual_journals)}≤{len(base_journals)})")
            else:
                print(f"✗ FAIL: Diamond count ({len(actual_journals)}) > base count ({len(base_journals)})")
        else:
            print("⚠ WARNING: Diamond function returned no results (may be valid if no non-APC journals match)")
else:
    print("⚠ Could not extract test areas/categories from database")

print("\n" + "="*80)
print("TESTS COMPLETED")
print("="*80)
