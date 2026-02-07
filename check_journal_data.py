from impl import JournalQueryHandler

jh = JournalQueryHandler()
jh.setDbPathOrUrl('./relational.db')
df = jh.getAllJournals()

print(f'Total journals: {len(df)}')
print(f'Columns: {df.columns.tolist()}')
print(df.head())
