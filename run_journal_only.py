from Handlers import JournalUploadHandler

handler = JournalUploadHandler()
handler.pushDataToDb("path_to_datafile.db")
print("Data pushed to database.")