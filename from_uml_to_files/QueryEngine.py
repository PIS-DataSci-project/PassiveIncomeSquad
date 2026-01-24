#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
from os import sep # for testing 
from posixpath import sep # for testing 
import pandas as pd 
from typing import Set, Dict, List
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler
import sqlite3

#------------------------------------------------
#BasicBasicQueryEngine
#------------------------------------------------

#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine: #Fahmida
    """
    UML class: BasicQueryEngine
    Coordinates multiple QueryHandler objects and combines their results.
    """

    def __init__(self):
        # UML: journalQuery : JournalQueryHandler [0..*]
        self.journalQuery = []

        # UML: categoryQuery : CategoryQueryHandler [0..*]
        self.categoryQuery = []

    # ---------------------------------------------------------
    #  METHODS
    # ---------------------------------------------------------

    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear() # remove all elements from the list
        return True # indicate success
    
    def cleanCategoryHandlers(self) -> bool: #Claudia
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear()
        return True
    
    def addJournalHandler(self, handler: JournalQueryHandler) -> bool:  # River
        self.journalQuery.append(handler)
        return True

    def addCategoryHandler(self, handler: CategoryQueryHandler) -> bool:  # River
        self.categoryQuery.append(handler)
        return True
    
    def getCategoriesByJournalId(self, journal_id) -> list: # Claudia
        """
        Get all Category objects for journal identifiers.
        Transforms DataFrames from CategoryQueryHandler into Category objects.
        """
        if isinstance(journal_id, str):
            journal_ids = [journal_id]
        else:
            journal_ids = journal_id
        
        categories = []
        for handler in self.categoryQuery:
            for journal_id in journal_ids:
                cat_df = handler.getCategoriesByJournalId(journal_id)
                if cat_df is not None and not cat_df.empty:
                    for _, row in cat_df.iterrows():
                        cat = Category(
                            identifiers=[str(row['category_id'])],
                            quartile=str(row.get('quartile', ''))
                        )
                        categories.append(cat)
        
        # Remove duplicates based on category_id
        unique_categories = []
        seen_ids = set()
        for cat in categories:
            cat_id = cat.getIds()[0] if cat.getIds() else None
            if cat_id and cat_id not in seen_ids:
                seen_ids.add(cat_id)
                unique_categories.append(cat)
        
        return unique_categories

    # ---------------------------------------------------------
    # GET ENTITIES BY ID
    # ---------------------------------------------------------

    def getAreasByJournalId(self, journal_id) -> list: # Claudia
        """
        Get all Area objects for journal identifiers.
        Transforms DataFrames from CategoryQueryHandler into Area objects.
        """
        if isinstance(journal_id, str):
            journal_ids = [journal_id]
        else:
            journal_ids = journal_id
        
        areas = []
        for handler in self.categoryQuery:
            for journal_id in journal_ids:
                area_df = handler.getAreasByJournalId(journal_id)
                if area_df is not None and not area_df.empty:
                    for _, row in area_df.iterrows():
                        if 'area' in row and pd.notna(row['area']):
                            area_name = str(row['area']).strip()
                            if area_name:
                                area = Area(identifiers=[area_name])
                                areas.append(area)
        
        # Remove duplicates based on area identifier
        unique_areas = {}
        for area in areas:
            area_id = area.getIds()[0] if area.getIds() else None
            if area_id and area_id not in unique_areas:
                unique_areas[area_id] = area
        
        return list(unique_areas.values())
    
    def getEntityById(self, entity_id: str):
        """
        Search for entity by ID in all databases.
        Returns: Journal or Category, or None
        """
        if not entity_id:
            return None
            
        # 1. Search in journal handlers (Blazegraph)
        journal_dfs = []
        for handler in self.journalQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                journal_dfs.append(result_df)
        
        # Merge and remove duplicates from journal results
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Parse identifiers from the identifier field (may contain multiple IDs separated by "; ")
                identifiers = []
                if 'identifier' in row and pd.notna(row['identifier']):
                    id_str = str(row['identifier'])
                    identifiers = [id.strip() for id in id_str.split(';') if id.strip()]
                
                # Ensure the searched entity_id is in the identifiers list
                if entity_id not in identifiers:
                    identifiers.append(entity_id)
                
                # Parse languages from the language field (may contain multiple languages)
                languages = []
                if 'language' in row and pd.notna(row['language']):
                    lang_str = str(row['language'])
                    languages = [lang.strip() for lang in lang_str.split(',') if lang.strip()]
                
                # Get categories and areas using helper methods
                categories = self.getCategoriesByJournalId(identifiers)
                areas = self.getAreasByJournalId(identifiers)
                
                # Convert boolean strings to actual booleans
                seal = False
                if 'seal' in row:
                    if isinstance(row['seal'], str):
                        seal = row['seal'].lower() == 'true'
                    else:
                        seal = bool(row['seal'])
                
                apc = False
                if 'apc' in row:
                    if isinstance(row['apc'], str):
                        apc = row['apc'].lower() == 'true'
                    else:
                        apc = bool(row['apc'])
                
                return Journal(
                    identifiers=identifiers,
                    title=str(row.get('title', '')),
                    language=languages,
                    seal=seal,
                    license=str(row.get('license', '')),
                    apc=apc,
                    publisher=str(row.get('publisher', '')),
                    categories=categories,
                    areas=areas
                )
        
        # 2. Search in category handlers (SQLite)
        category_dfs = []
        for handler in self.categoryQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                category_dfs.append(result_df)
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Return Category
                identifiers = []
                if 'category_id' in row:
                    identifiers.append(str(row['category_id']))
                if 'identifiers' in row and pd.notna(row['identifiers']):
                    identifiers.append(str(row['identifiers']))
                
                return Category(
                    identifiers=list(set(identifiers)) if identifiers else [entity_id],
                    quartile=str(row.get('quartile', ''))
                )
        
        # 3. If not found as journal in Blazegraph or as category, check if we have category/area data for this identifier
        categories = self.getCategoriesByJournalId(entity_id)
        areas = self.getAreasByJournalId(entity_id)
        
        if categories or areas:
            # Found category/area data, return minimal Journal object
            return Journal(
                identifiers=[entity_id],
                title="",
                language=[],
                seal=False,
                license="",
                apc=False,
                publisher="",
                categories=categories,
                areas=areas
            )
        
        # 4. Not found in any database
        return None
       
       
    # ============================================
    # JOURNAL-RELATED METHODS (Polina)
    # ============================================
    def getAllJournals(self) -> list:
        #Get all the journals
        all_dfs = [handler.getAllJournals() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsWithTitle(self, partialTitle: str) -> list:
        # find all the journals with a partial title match
        all_dfs = [handler.getJournalsWithTitle(partialTitle) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsPublishedBy(self, partialName: str) -> list:
        #get the journals published by a publisher
        all_dfs = [handler.getJournalsPublishedBy(partialName) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]
 
    # ---------------------------------------------------------

    def getJournalsWithLicense(self, licenses: set) -> list:
        # get all the journals with a license
        all_dfs = [handler.getJournalsWithLicense(licenses) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()

        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsWithAPC(self) -> list:
        #get all the journals with APC
        all_dfs = [handler.getJournalsWithAPC() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------
    
    def getJournalsWithDOAJSeal(self) -> list:
        # get all the journals with DOAJ Seal
        all_dfs = [handler.getJournalsWithDOAJSeal() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
    
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]
        
    # ---------------------------------------------------------
    # CATEGORY-RELATED METHODS (Fahmida)
    # ---------------------------------------------------------

    def getAllCategories(self) -> list:
        """
        UML: getAllCategories() : list[Category]
        Returns all categories with no repetitions.
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getAllCategories()
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAllAreas(self) -> list:
        """
        Returns all areas from Scimago, with no repetitions.
        """

        dfs = []

        # Call getAllAreas on every CategoryQueryHandler
        for handler in self.categoryQuery:
            df = handler.getAllAreas()  # returns column 'area'
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        # Merge and remove duplicates
        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        # Convert rows into Area objects
        return [
            Area(
                identifiers={row["area"]}  # <- this is the correct column
            )
            for _, row in merged.iterrows()
        ]


    # ---------------------------------------------------------

    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """
        UML: getCategoriesWithQuartile(quartiles : set[string]) : list[Category]
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getCategoriesAssignedToAreas(self, area_ids: set) -> list:
        """
        UML: getCategoriesAssignedToAreas(area_ids : set[string]) : list[Category]
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAreasAssignedToCategories(self, category_ids: set) -> list:
        """
        UML: getAreasAssignedToCategories(category_ids : set[string]) : list[Area]
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getAreasAssignedToCategories(category_ids)
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Area(
                identifiers={row["area"]}
            )
            for _, row in merged.iterrows()
        ]
    
#------------------------------------------------
#FullQueryEngine
#------------------------------------------------
class FullQueryEngine(BasicQueryEngine):
    """
    FullQueryEngine = “跨源拼接查询”的 QueryEngine。

    它做的事不是“替代” BasicQueryEngine，而是在 BasicQueryEngine 的基础上做 mashup：
    1) 先用 CategoryQueryHandler（SQLite）查出一批 journal identifiers（ISSN/EISSN）。
    2) 再用 JournalQueryHandler（图数据库 / SPARQL）把这些 identifiers 对应的 journals 查出来。
    3) 最后返回 Journal 对象列表（领域对象），而不是 DataFrame。

    设计风格对齐 BasicQueryEngine：
    - handler 负责查 df
    - engine 负责把 df 变成对象（复用类似 _add_journals_from_df 的“翻译器”思路）
    """

    def __init__(self, journalQuery=None, categoryQuery=None):
        # 原 River_full.py 的 super().__init__(journalQuery or [], categoryQuery or [])
        # 但你现有 BasicQueryEngine.__init__ 不接参数，所以这里做“等价初始化”：
        super().__init__()
        if journalQuery:
            self.journalQuery.extend(journalQuery)
        if categoryQuery:
            self.categoryQuery.extend(categoryQuery)

    # --------------------------
    # 1) Parse：你要求“必须用”
    # --------------------------
    def _parse_list_field(self, raw) -> List[str]:
        """
        把数据库/df 里可能出现的“粘连字符串字段”拆成 list。

        为什么需要：
        - identifiers 可能是 "1234-5678; 8765-4321" 或 "1234-5678,8765-4321"
        - language 可能是 "English; Italian"
        - 有时也可能是 None / 空串

        我们不处理 bool（按你的要求），这里只做“字符串拆分”。
        """
        if raw is None:
            return []
        text = str(raw).strip()
        if not text:
            return []

        # 兼容两种常见分隔符：; 和 ,
        text = text.replace(";", ",")
        parts = [p.strip() for p in text.split(",")]
        return [p for p in parts if p]

    # --------------------------------------------
    # 2) 辅助：从 categories df “翻译”出 identifiers 集合
    # --------------------------------------------
    def _add_identifiers_from_categories_df(self, df: pd.DataFrame, identifiers: Set[str]) -> None:
        if df is None or df.empty:
            return

        # 兼容列名：有的地方叫 identifiers，有的地方可能叫 identifier
        col = "identifiers" if "identifiers" in df.columns else "identifier"
        if col not in df.columns:
            return

        for _, row in df.iterrows():
            for one_id in self._parse_list_field(row.get(col)):
                identifiers.add(one_id)

    # ---------------------------------------------------
    # 3) 辅助：从 journals df 中挑出“匹配 identifiers 的行”
    # ---------------------------------------------------
    def _add_journals_matching_identifiers_from_df(
        self,
        df: pd.DataFrame,
        wanted_identifiers: Set[str],
        journal_map: Dict[str, Journal],
    ) -> None:
        if df is None or df.empty or not wanted_identifiers:
            return

        id_col = "identifier" if "identifier" in df.columns else "identifiers"
        if id_col not in df.columns:
            return

        for _, row in df.iterrows():
            row_ids = self._parse_list_field(row.get(id_col))
            if not row_ids:
                continue

            hit = any(one_id in wanted_identifiers for one_id in row_ids)
            if not hit:
                continue

            key = row_ids[0]

            if key not in journal_map:
                journal_map[key] = Journal(
                    identifiers=row_ids,
                    title=row.get("title", ""),
                    language=self._parse_list_field(row.get("language")),
                    seal=row.get("seal", False),      # bool 暂且不处理，直接传
                    license=row.get("license", ""),
                    apc=row.get("apc", False),        # bool 暂且不处理，直接传
                    publisher=row.get("publisher", None),
                )

    # ==========================
    # Mashup 查询 1
    # ==========================
    def getJournalsInCategoriesWithQuartile(
        self,
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 2
    # ==========================
    def getJournalsInAreasWithLicense(
        self,
        area_ids: Set[str],
        licenses: Set[str],
    ) -> List[Journal]:
        if not area_ids or not licenses:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 3
    # ==========================
    def getJournalsInAreasAndCategoriesWithQuartile(
        self,
        area_ids: Set[str],
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not area_ids or not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]
            if "quartile" in df.columns:
                df = df[df["quartile"].isin(quartiles)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())