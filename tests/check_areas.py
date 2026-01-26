import tempfile
import os
from impl import CategoryUploadHandler, CategoryQueryHandler

# Create temp db
tf = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
tf.close()
path = tf.name

# Upload data
h = CategoryUploadHandler()
h.setDbPathOrUrl(path)
h.pushDataToDb('data/scimago.json')

# Query areas
qh = CategoryQueryHandler()
qh.setDbPathOrUrl(path)
areas_df = qh.getAllAreas()

print(f'Unique area entries in DB: {areas_df["area"].nunique()}')
print('\nAll unique areas:')
for area in sorted(areas_df["area"].unique()):
    print(f'  - {area}')

# Clean up
os.unlink(path)
