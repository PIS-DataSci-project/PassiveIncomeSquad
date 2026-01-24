from impl import JournalUploadHandler

# Configure Blazegraph endpoint
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

# Create handler and upload
jou = JournalUploadHandler()
jou.setDbPathOrUrl(grp_endpoint)

print("Uploading journals to Blazegraph...")
print(f"Endpoint: {grp_endpoint}")
print(f"File: data/doaj.csv")
print()

result = jou.pushDataToDb("data/doaj.csv")

if result:
    print("✓ Upload completed successfully!")
else:
    print("✗ Upload failed")
