from Handlers import CategoryUploadHandler

handler = CategoryUploadHandler()
handler.setdbPathOrUrl("relational.db")
print(handler.pushDataToDb("data/scimago-json.json"))
