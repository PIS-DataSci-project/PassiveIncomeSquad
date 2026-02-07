from River_imply import JournalQueryHandler, CategoryQueryHandler, FullQueryEngine

# === 配置路径（按你当前项目默认）===
relational = "./relational.db"
sparql_endpoint = "http://192.168.78.152:9999/blazegraph/sparql"

# === 初始化 handlers ===
jq = JournalQueryHandler()
jq.setDbPathOrUrl(sparql_endpoint)

cq = CategoryQueryHandler()
cq.setDbPathOrUrl(relational)

# === FullQueryEngine ===
engine = FullQueryEngine()
engine.addJournalHandler(jq)
engine.addCategoryHandler(cq)

# === 测试输入（你可替换成你的实际预期集合）===
category_ids = {"Hematology", "Oncology"}          # 示例
quartiles = {"Q1"}                                 # 示例
area_ids = {"Medicine"}                            # 示例

# --- 测试 1: getJournalsInCategoriesWithQuartile ---
journals_q = engine.getJournalsInCategoriesWithQuartile(category_ids, quartiles)

all_ids = set()
for j in journals_q:
    for i in j.getIds():
        all_ids.add(i)

print("=== getJournalsInCategoriesWithQuartile ===")
print("Journal count:", len(journals_q))
print("Unique identifier count:", len(all_ids))
for j in journals_q:
    print("  Journal IDs:", j.getIds())

# --- 测试 2: getDiamondJournalsInAreasAndCategoriesWithQuartile ---
journals_d = engine.getDiamondJournalsInAreasAndCategoriesWithQuartile(
    area_ids, category_ids, quartiles
)

all_ids_d = set()
for j in journals_d:
    for i in j.getIds():
        all_ids_d.add(i)

print("\n=== getDiamondJournalsInAreasAndCategoriesWithQuartile ===")
print("Journal count:", len(journals_d))
print("Unique identifier count:", len(all_ids_d))
for j in journals_d:
    print("  Journal IDs:", j.getIds())
