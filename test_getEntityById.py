
from impl import CategoryQueryHandler
from impl import JournalQueryHandler
from QueryEngine import BasicQueryEngine

rel_path = "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(rel_path)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

# Finally, create a advanced mashup object for asking
# about data
que = BasicQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

result_q3 = que.getEntityById("Medicine")
result_q4 = que.getEntityById("2532-8816")

print(result_q3)