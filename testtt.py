from os import sep

from matplotlib.pylab import rint
from impl import JournalQueryHandler, CategoryQueryHandler, BasicQueryEngine
from impl import Journal, Category, Area
from impl import FullQueryEngine

def print_journal(journal):
    if journal is None:
        print("None")
        return
    
    try:
        print(f"Title: {journal.getTitle()}")
    except UnicodeEncodeError:
        print(f"Title: [Unicode encoding error - cannot display]")
    print(f"IDs: {journal.getIds()}")
    print(f"Publisher: {journal.getPublisher()}")
    print(f"Languages: {journal.getLanguage()}")
    print(f"DOAJ Seal: {journal.hasDOAJSeal()}")
    print(f"License: {journal.getLicense()}")
    print(f"Has APC: {journal.hasAPC()}")
    print(f"Categories:({journal.getCategories()})")
    print(f"Areas ({journal.getAreas()}):")
        
journal = "data" + sep + "doaj.csv"
category = "data" + sep + "scimago.json"
relational = "." + sep + "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
    
jq = JournalQueryHandler()
jq.setDbPathOrUrl(grp_endpoint)
cq = CategoryQueryHandler()
cq.setDbPathOrUrl(relational)

fq = FullQueryEngine()
fq.cleanJournalHandlers()
fq.cleanCategoryHandlers()
fq.addJournalHandler(jq)
fq.addCategoryHandler(cq)

result = fq.getEntityById("just_a_test")
if result is None:
    print("Test passed: getEntityById returned None for non-existent ID")
else:
    print("Test failed: expected None but got", result)
    
# USAGE 
cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(relational)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

# Finally, create a advanced mashup object for asking
# about data
que = FullQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

search_id = "2096-6652"
print("\nSearching for journal with ID:", search_id)
print("=" * 60)
result_q4 = que.getEntityById(search_id)

if result_q4 is None:
    print("Result is None - journal not found in any database")
else:
    print_journal(result_q4)