import sqlite3
from impl import CategoryQueryHandler

# Test CategoryQueryHandler methods
cat_handler = CategoryQueryHandler('relational.db')

# Test getCategoriesWithQuartile
df = cat_handler.getCategoriesWithQuartile({'Q1'})
print('getCategoriesWithQuartile columns:', df.columns.tolist())
print('Sample rows:', df.head(2).to_dict('records') if not df.empty else 'Empty')

# Test getCategoriesAssignedToAreas
df2 = cat_handler.getCategoriesAssignedToAreas({'Computer Science'})
print('getCategoriesAssignedToAreas columns:', df2.columns.tolist())
print('Sample rows:', df2.head(2).to_dict('records') if not df2.empty else 'Empty')

# Test getById which does include identifiers
df3 = cat_handler.getById('COMPINT')
print('getById columns:', df3.columns.tolist())
print('Sample rows:', df3.head(2).to_dict('records') if not df3.empty else 'Empty')