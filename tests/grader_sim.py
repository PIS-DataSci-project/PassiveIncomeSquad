import sys
from impl import FullQueryEngine, JournalQueryHandler, CategoryQueryHandler


def check_method(obj, method):
    if not hasattr(obj, method):
        print(f"FAIL {obj.__class__.__name__} missing method '{method}'")
        return False
    try:
        getattr(obj, method)()
        print(f"PASS {obj.__class__.__name__}.{method}() exists and is callable")
        return True
    except Exception as e:
        print(f"FAIL {obj.__class__.__name__}.{method}() raised: {e}")
        return False


def check_count(name, result, expected):
    actual = len(result) if hasattr(result, "__len__") else 0
    if actual == expected:
        print(f"PASS {name}: {actual} (as expected)")
    elif actual > expected:
        print(f"FAIL {name}: {actual} > expected {expected}")
    else:
        print(f"FAIL {name}: {actual} < expected {expected}")


# Expected values for the full relational.db + full graph dataset currently used
# by this simulator. These are not the tiny fixture/sample counts.
EXPECTED = {
    "getAllCategories": 310,
    "getAllAreas": 27,
    "getCategoriesWithQuartile": 308,
    "getCategoriesAssignedToAreas": 282,
    "getAreasAssignedToCategories": 24,
    "getJournalsInCategoriesWithQuartile": 36,
    "getDiamondJournalsInAreasAndCategoriesWithQuartile": 0,
    "getJournalsInAreasWithLicense": 236,
}


if __name__ == "__main__":
    try:
        # Use Blazegraph endpoint for journals
        journal_handler = JournalQueryHandler("http://192.168.78.117:9999/blazegraph/sparql")
        category_handler = CategoryQueryHandler("relational.db")
        qe = FullQueryEngine(journalQuery=[journal_handler], categoryQuery=[category_handler])
    except Exception as e:
        print(f"FAIL Could not instantiate FullQueryEngine: {e}")
        sys.exit(1)

    # Helper to deduplicate categories by category_id
    def dedup_categories(res):
        if not res:
            return res
        seen = set()
        deduped = []
        for cat in res:
            cid = cat.identifiers[0] if hasattr(cat, "identifiers") and cat.identifiers else None
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(cat)
        return deduped

    # 1. getAllCategories
    res = qe.getAllCategories()
    res = dedup_categories(res)
    check_count("getAllCategories", res, EXPECTED["getAllCategories"])

    # 2. getAllAreas
    res = qe.getAllAreas()
    check_count("getAllAreas", res, EXPECTED["getAllAreas"])

    # 3. getCategoriesWithQuartile
    res = qe.getCategoriesWithQuartile({"Q1"})
    res = dedup_categories(res)
    check_count("getCategoriesWithQuartile", res, EXPECTED["getCategoriesWithQuartile"])

    # 4. getCategoriesAssignedToAreas
    res = qe.getCategoriesAssignedToAreas({"Medicine"})
    res = dedup_categories(res)
    check_count("getCategoriesAssignedToAreas", res, EXPECTED["getCategoriesAssignedToAreas"])

    # 5. getAreasAssignedToCategories
    res = qe.getAreasAssignedToCategories({"Artificial Intelligence"})
    check_count("getAreasAssignedToCategories", res, EXPECTED["getAreasAssignedToCategories"])

    # 6. getJournalsInCategoriesWithQuartile
    res = qe.getJournalsInCategoriesWithQuartile({"Oncology"}, {"Q1"})
    check_count("getJournalsInCategoriesWithQuartile", res, EXPECTED["getJournalsInCategoriesWithQuartile"])

    # 7. getDiamondJournalsInAreasAndCategoriesWithQuartile
    res = qe.getDiamondJournalsInAreasAndCategoriesWithQuartile({"Medicine"}, {"Oncology"}, {"Q1"})
    check_count(
        "getDiamondJournalsInAreasAndCategoriesWithQuartile",
        res,
        EXPECTED["getDiamondJournalsInAreasAndCategoriesWithQuartile"],
    )

    # 8. getJournalsInAreasWithLicense
    res = qe.getJournalsInAreasWithLicense({"Computer Science"}, {"CC BY"})
    check_count("getJournalsInAreasWithLicense", res, EXPECTED["getJournalsInAreasWithLicense"])

    # 9. getEntityById: check methods
    journal = qe.getEntityById("2532-8816")
    if journal:
        check_method(journal, "getLanguages")
        check_method(journal, "getLicence")
    else:
        print("FAIL getEntityById did not return a Journal for '2532-8816'")
