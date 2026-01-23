import pandas as pd

# ✅ 强制保证 Journal/Category/Area 存在
try:
    from Entities import Journal, Category, Area
except Exception as e:
    raise ImportError(
        "Cannot import Journal/Category/Area from Entities.py.\n"
        "Check that Entities.py exists and is on PYTHONPATH.\n"
        "If your file is in a subfolder, adjust import, e.g.:\n"
        "  from src.Entities import Journal, Category, Area\n"
        f"\nOriginal error: {e}"
    )

# ✅ 肉眼自检：如果你愿意，可以临时打开这一行看输出
# print("Loaded entities:", Journal, Category, Area)



class BasicQueryEngine:  # Fahmida
    def __init__(self):
        self.journalQuery = []
        self.categoryQuery = []

    def cleanJournalHandlers(self) -> bool:  # Claudia
        had_handlers = bool(self.journalQuery)
        self.journalQuery = []
        return had_handlers

    def cleanCategoryHandlers(self) -> bool:  # River
        had_handlers = bool(self.categoryQuery)
        self.categoryQuery = []
        return had_handlers

    # ✅ 用“鸭子类型”判断，不依赖 JournalQueryHandler 这个名字
    def addJournalHandler(self, handler) -> bool:
        if handler is None:
            return False
        required = ["getById", "getJournalsWithTitle"]
        if all(hasattr(handler, m) for m in required):
            self.journalQuery.append(handler)
            return True
        return False

    # ✅ 同上：不依赖 CategoryQueryHandler 这个名字
    def addCategoryHandler(self, handler) -> bool:
        if handler is None:
            return False
        required = ["getById", "getAllCategories", "getAllAreas"]
        if all(hasattr(handler, m) for m in required):
            self.categoryQuery.append(handler)
            return True
        return False

    def _split_values(self, value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return []
        if isinstance(value, list):
            return [item for item in value if item]
        if not isinstance(value, str):
            return [str(value)]
        normalized = value.replace(";", ",")
        return [item.strip() for item in normalized.split(",") if item.strip()]

    def _parse_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return False
        if isinstance(value, str):
            return value.strip().lower() in {"true", "yes", "1"}
        return bool(value)

    def _journals_from_df(self, df: pd.DataFrame) -> list:
        journals = []
        if df is None or df.empty:
            return journals
        for _, row in df.iterrows():
            identifiers = self._split_values(row.get("identifier"))
            title = row.get("title", "")
            language = self._split_values(row.get("language"))
            publisher = row.get("publisher", "")
            seal = self._parse_bool(row.get("seal"))
            license_value = row.get("license", "")
            apc = self._parse_bool(row.get("apc"))
            journals.append(
                Journal(
                    identifiers=identifiers,
                    title=title,
                    language=language,
                    seal=seal,
                    license=license_value,
                    apc=apc,
                    publisher=publisher,
                )
            )
        return journals

    def _categories_from_df(self, df: pd.DataFrame) -> list:
        categories = []
        if df is None or df.empty:
            return categories
        for _, row in df.iterrows():
            identifiers = self._split_values(row.get("identifiers"))
            category_id = row.get("category_id")
            quartile = row.get("quartile")
            if category_id:
                identifiers.append(str(category_id))
            categories.append(Category(identifiers=identifiers, quartile=quartile))
        return categories

    def _areas_from_df(self, df: pd.DataFrame) -> list:
        areas = []
        if df is None or df.empty:
            return areas
        for _, row in df.iterrows():
            area_id = row.get("area")
            if area_id is None or (isinstance(area_id, float) and pd.isna(area_id)):
                continue
            areas.append(Area([str(area_id)]))
        return areas

    def _dedupe_journals(self, journals: list) -> list:
        seen = set()
        unique = []
        for journal in journals:
            ids = tuple(journal.getIds())
            if ids in seen:
                continue
            seen.add(ids)
            unique.append(journal)
        return unique

    def _dedupe_entities(self, entities: list) -> list:
        seen = set()
        unique = []
        for entity in entities:
            ids = tuple(entity.getIds())
            if ids in seen:
                continue
            seen.add(ids)
            unique.append(entity)
        return unique

    def getEntityById(self, entity_id: str):  # Claudia
        if not entity_id:
            return None

        # 1) Journals first
        for handler in self.journalQuery:
            df = handler.getById(entity_id)
            journals = self._journals_from_df(df)
            if journals:
                return journals[0]

        # 2) Categories next
        for handler in self.categoryQuery:
            df = handler.getById(entity_id)
            categories = self._categories_from_df(df)
            if categories:
                return categories[0]

        # 3) Areas fallback (check if entity_id exists in area table)
        for handler in self.categoryQuery:
            df = handler.getAllAreas()
            if (
                df is not None
                and not df.empty
                and "area" in df.columns
                and entity_id in df["area"].values
            ):
                return Area([entity_id])

        return None

    def getAllJournals(self) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            # handler.getAllJournals() 需要存在，否则会 AttributeError
            if hasattr(handler, "getAllJournals"):
                journals.extend(self._journals_from_df(handler.getAllJournals()))
        return self._dedupe_journals(journals)

    def getJournalsWithTitle(self, partialTitle: str) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            journals.extend(self._journals_from_df(handler.getJournalsWithTitle(partialTitle)))
        return self._dedupe_journals(journals)

    def getJournalsPublishedBy(self, partialName: str) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            if hasattr(handler, "getJournalsPublishedBy"):
                journals.extend(self._journals_from_df(handler.getJournalsPublishedBy(partialName)))
        return self._dedupe_journals(journals)

    def getJournalsWithLicense(self, licenses) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            if hasattr(handler, "getJournalsWithLicense"):
                journals.extend(self._journals_from_df(handler.getJournalsWithLicense(licenses)))
        return self._dedupe_journals(journals)

    def getJournalsWithAPC(self) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            if hasattr(handler, "getJournalsWithAPC"):
                journals.extend(self._journals_from_df(handler.getJournalsWithAPC()))
        return self._dedupe_journals(journals)

    def getJournalsWithDOAJSeal(self) -> list:  # Polina
        journals = []
        for handler in self.journalQuery:
            if hasattr(handler, "getJournalsWithDOAJSeal"):
                journals.extend(self._journals_from_df(handler.getJournalsWithDOAJSeal()))
        return self._dedupe_journals(journals)

    def getAllCategories(self) -> list:  # Fahmida
        categories = []
        for handler in self.categoryQuery:
            categories.extend(self._categories_from_df(handler.getAllCategories()))
        return self._dedupe_entities(categories)

    def getAllAreas(self) -> list:  # Fahmida
        areas = []
        for handler in self.categoryQuery:
            areas.extend(self._areas_from_df(handler.getAllAreas()))
        return self._dedupe_entities(areas)

    def getCategoriesWithQuartile(self, quartiles) -> list:  # Fahmida
        categories = []
        for handler in self.categoryQuery:
            if hasattr(handler, "getCategoriesWithQuartile"):
                categories.extend(self._categories_from_df(handler.getCategoriesWithQuartile(quartiles)))
        return self._dedupe_entities(categories)

    def getCategoriesAssignedToAreas(self, area_ids) -> list:  # Fahmida
        categories = []
        for handler in self.categoryQuery:
            if hasattr(handler, "getCategoriesAssignedToAreas"):
                categories.extend(self._categories_from_df(handler.getCategoriesAssignedToAreas(area_ids)))
        return self._dedupe_entities(categories)

    def getAreasAssignedToCategories(self, category_ids) -> list:  # Fahmida
        areas = []
        for handler in self.categoryQuery:
            if hasattr(handler, "getAreasAssignedToCategories"):
                areas.extend(self._areas_from_df(handler.getAreasAssignedToCategories(category_ids)))
        return self._dedupe_entities(areas)



#Subclass --> FullQueryEngine(BasicQueryEngine) 