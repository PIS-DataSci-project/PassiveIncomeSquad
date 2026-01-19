from Handlers import JournalUploadHandler

handler = JournalUploadHandler()
handler.serializeToTTL("data/doaj-csv.csv", "doaj.ttl")

