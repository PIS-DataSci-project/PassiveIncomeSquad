#!/usr/bin/env python
"""
Debug script to trace through the handler methods
"""

import sqlite3
from impl import CategoryQueryHandler, JournalQueryHandler, FullQueryEngine

rel_db = './relational.db'

print("="*100)
print("DEBUGGING HANDLER METHODS")
print("="*100)

# Test CategoryQueryHandler
ch = CategoryQueryHandler()
ch.setDbPathOrUrl(rel_db)

print("\n--- Testing CategoryQueryHandler ---")

# Test getCategoriesWithQuartile
print("\n1. getCategoriesWithQuartile(['Q1']):")
df = ch.getCategoriesWithQuartile({'Q1'})
print(f"   Type: {type(df)}")
if df is not None and not df.empty:
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")
    print(f"   Sample:\n{df.head()}")
else:
    print(f"   Empty DataFrame")

# Test JournalQueryHandler
jh = JournalQueryHandler()
jh.setDbPathOrUrl(rel_db)

print("\n2. getAllJournals():")
df = jh.getAllJournals()
print(f"   Type: {type(df)}")
if df is not None and not df.empty:
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")
    print(f"   Sample:\n{df.head()}")
else:
    print(f"   Empty DataFrame")

# Test the function
print("\n--- Testing Full Function ---")
engine = FullQueryEngine()
engine.journalQuery.append(jh)
engine.categoryQuery.append(ch)

result = engine.getJournalsInCategoriesWithQuartile({'Accounting'}, {'Q1'})
print(f"\ngetJournalsInCategoriesWithQuartile({'Accounting'}, {'Q1'}):")
print(f"  Returned: {len(result)} journals")
