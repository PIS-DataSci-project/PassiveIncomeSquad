from os import sep


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
    print(f"Languages: {journal.getLanguages()}")
    print(f"DOAJ Seal: {journal.hasDOAJSeal()}")
    print(f"License: {journal.getLicense()}")
    print(f"Has APC: {journal.hasAPC()}")
    
    # Print categories with their details
    categories = journal.getCategories()
    if categories:
        print(f"Categories ({len(categories)}):")
        for cat in categories:
            cat_ids = cat.getIds()
            quartile = cat.getQuartile()
            print(f"  - {cat_ids[0] if cat_ids else 'N/A'} (Quartile: {quartile})")
    else:
        print("Categories: []")
    
    # Print areas with their details
    areas = journal.getAreas()
    if areas:
        print(f"Areas ({len(areas)}):")
        for area in areas:
            area_ids = area.getIds()
            print(f"  - {area_ids[0] if area_ids else 'N/A'}")
    else:
        print("Areas: []")
        
journal = "data" + sep + "doaj.csv"
category = "data" + sep + "scimago.json"
relational = "." + sep + "relational.db"
grp_endpoint = "http://172.20.10.2:9999/blazegraph/sparql"

   
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