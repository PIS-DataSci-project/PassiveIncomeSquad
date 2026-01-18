import json
import pandas as pd

# -----------------------------
# Step 1: Set JSON file path
# -----------------------------
json_file = "data/scimago-json.json"  # file path

# -----------------------------
# Step 2: Load JSON
# -----------------------------
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)  # data is a list of dictionaries

# -----------------------------
# Step 3: Flatten nested 'categories'
# -----------------------------
df = pd.json_normalize(
    data,
    record_path="categories",      # nested list we want as rows
    meta=["identifiers", "areas"]  # keep parent info
)

# -----------------------------
# Step 4: Inspect the table
# -----------------------------
print("📊 First 5 rows of the table:")
print(df.head())

print("\n📌 Columns:")
print(df.columns)

print("\n🧮 Shape (rows x columns):")
print(df.shape)

# -----------------------------
# Step 5: Save as CSV for easier inspection
# -----------------------------
df.to_csv("categories_debug.csv", index=False)
print("\n✅ CSV saved as 'categories_debug.csv'. Open it to see the full table.")
