from impl import CategoryUploadHandler
import os

# Remove the old database
if os.path.exists('relational.db'):
    os.remove('relational.db')
    print('Removed old relational.db')

# Upload data with the fix
u = CategoryUploadHandler()
u.setDbPathOrUrl('relational.db')
success = u.pushDataToDb('data/scimago.json')

if success:
    print('Data uploaded successfully!')
else:
    print('Upload failed!')

# Verify the fix
from impl import CategoryQueryHandler

qh = CategoryQueryHandler(dbPathOrUrl='relational.db')
result = qh.getCategoriesAssignedToAreas({'Business, Management and Accounting'})
print(f'\nCategories for Business, Management and Accounting: {len(result)}')

# Check if Pollution is now included
pollution_rows = result[result['category_id'] == 'Pollution']
if not pollution_rows.empty:
    print('✓ Pollution is now included!')
else:
    print('✗ Pollution still missing')
