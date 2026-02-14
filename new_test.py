# Setup (from exemplar_execution.py)
from impl import * 

rel_path = "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(rel_path)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

que = FullQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

# Test queries
result1 = que.getJournalsInCategoriesWithQuartile({"AI"}, {"Q1"})
print(f"Found {len(result1)} journals")  # Should return > 0

result2 = que.getJournalsInAreasWithLicense({"Computer Science"}, {"CC-BY"})
print(f"Found {len(result2)} journals")  # Should return > 0

result3 = que.getJournalsInAreasAndCategoriesWithQuartile(
    {"Computer Science"}, {"AI"}, {"Q1"}
)
print(f"Found {len(result3)} journals")  # Should return > 0