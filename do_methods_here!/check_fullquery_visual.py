from River_imply import FullQueryEngine

# 你自己创建 engine（和你 test.py 一样）
engine = FullQueryEngine()

# 如果你平时是在别处 add handler，这里照抄
# 例如：
# engine.journalQuery.append(journalHandler)
# engine.categoryQuery.append(categoryHandler)


# ====== 你可以随便换成存在的数据 ======
AREA_IDS = {"12"}
CATEGORY_IDS = {"2402"}
QUARTILES = {"Q1"}
# ======================================


print("\n==============================")
print("MASHUP 1: getJournalsInCategoriesWithQuartile")
print("==============================")

journals = engine.getJournalsInCategoriesWithQuartile(CATEGORY_IDS, QUARTILES)

print("Returned journals:", len(journals))
print("\nFirst 5 journals:")

for j in journals[:5]:
    print("IDs:", getattr(j, "identifiers", None))
    print("Title:", getattr(j, "title", None))
    print("APC:", getattr(j, "apc", None))
    print("---")


print("\n==============================")
print("MASHUP 3 (BASE)")
print("==============================")

base = engine.getJournalsInAreasAndCategoriesWithQuartile(
    AREA_IDS,
    CATEGORY_IDS,
    QUARTILES,
)

print("Base journal count:", len(base))


print("\n==============================")
print("DIAMOND QUERY")
print("==============================")

diamond = engine.getDiamondJournalsInAreasAndCategoriesWithQuartile(
    AREA_IDS,
    CATEGORY_IDS,
    QUARTILES,
)

print("Diamond journal count:", len(diamond))


print("\nFirst 5 diamond journals:")
for j in diamond[:5]:
    print("IDs:", getattr(j, "identifiers", None))
    print("APC:", getattr(j, "apc", None))
    print("---")


print("\n==============================")
print("DIAMOND CHECK")
print("==============================")

if len(diamond) >= len(base):
    print("⚠️ Diamond query is NOT smaller than base query.")
    print("This means APC filtering probably did not work.")
else:
    print("✓ Diamond query looks filtered correctly.")


print("\n==============================")
print("IDENTIFIER CHECK")
print("==============================")

all_ids = set()
for j in journals:
    ids = getattr(j, "identifiers", [])
    if ids:
        all_ids.update(ids)

print("Unique identifier count:", len(all_ids))
print("Example identifiers:", list(all_ids)[:10])
