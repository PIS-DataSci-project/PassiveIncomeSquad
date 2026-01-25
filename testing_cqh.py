# THIS WILL NOT WORK IF I DON'T have rdflib installed
# test_category_handler.py
# ------------------------
# Test file for CategoryQueryHandler (relational DB)
# No Graph DB dependencies
from impl_fahmy import CategoryQueryHandler

# ------------------------
# Configure database path
# ------------------------
db_path = "relational.db"  # Replace with your actual SQLite DB path

# ------------------------
# Initialize handler
# ------------------------
cqh = CategoryQueryHandler(dbPathOrUrl=db_path)

# ------------------------
# 1️⃣ Test getById()
# ------------------------
identifiers = "2658-6533"  # Replace with a valid identifiers from your DB
df_by_id = cqh.getById(identifiers)
print("=== getById() ===")
print(df_by_id)
print("\nRows returned:", len(df_by_id))

# ------------------------
# 2️⃣ Test getAllCategories()
# ------------------------
df_all = cqh.getAllCategories()
print("\n=== getAllCategories() (first 5 rows) ===")
print(df_all.head())
print("Total rows:", len(df_all))

# ------------------------
# 3️⃣ Test getAllAreas()
# ------------------------
df_areas = cqh.getAllAreas()
print("\n=== getAllAreas() (first 5 rows) ===")
print(df_areas.head())
print("Total rows:", len(df_areas))

# ------------------------
# 4️⃣ Test getCategoriesWithQuartile()
# ------------------------
quartiles = {"Q1", "Q2"}  # Example set of quartiles
df_quartile = cqh.getCategoriesWithQuartile(quartiles)
print("\n=== getCategoriesWithQuartile() ===")
print(df_quartile.head())
print("Rows returned:", len(df_quartile))

# ------------------------
# 5️⃣ Test getCategoriesAssignedToAreas()
# ------------------------
areas = {"Neuroscience", "Medicine"}  # Example area names
df_cat_areas = cqh.getCategoriesAssignedToAreas(areas)
print("\n=== getCategoriesAssignedToAreas() ===")
print(df_cat_areas.head())
print("Rows returned:", len(df_cat_areas))

# ------------------------
# 6️⃣ Test getAreasAssignedToCategories()
# ------------------------
category_ids = {"Oncology", "Pharmacology"}  # Example category IDs
df_area_cats = cqh.getAreasAssignedToCategories(category_ids)
print("\n=== getAreasAssignedToCategories() ===")
print(df_area_cats.head())
print("Rows returned:", len(df_area_cats))
