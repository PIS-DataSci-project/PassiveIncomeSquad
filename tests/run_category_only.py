from impl import CategoryUploadHandler

handler = CategoryUploadHandler()
handler.setDbPathOrUrl("relational.db")
print(handler.pushDataToDb("data/scimago-json.json"))
