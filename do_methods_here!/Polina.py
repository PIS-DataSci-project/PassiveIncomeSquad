#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
from typing import List, Dict
from Entities import Journal
from impl import JournalQueryHandler, CategoryQueryHandler
#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine:
    """
    This class corresponds to the UML class BasicQueryEngine.
    It coordinates multiple QueryHandler objects and combines their results.
    """

    def __init__(self):
        # UML: journalQuery : JournalQueryHandler [0..*]
        # In Python, [0..*] is represented by a list
        # This list will store OBJECTS of type JournalQueryHandler
        self.journalQuery = []

        # UML: categoryQuery : CategoryQueryHandler [0..*]
        # This list will store OBJECTS of type CategoryQueryHandler
        self.categoryQuery = []

    # ---------------------------------------------------------
    # CATEGORY-RELATED METHODS (assigned to Fahmida)
    # ---------------------------------------------------------

    def getAllCategories(self) -> list:
        """
        UML: getAllCategories() : list[Category]

        Returns all categories from Scimago Journal Rank,
        with no repetitions.
        """

        # This list will collect DataFrames returned by each handler
        dfs = []

        # Call the same method on ALL CategoryQueryHandler objects
        for handler in self.categoryQuery:
            # Each handler queries its own data source
            df = handler.getAllCategories()

            # We only keep non-empty results
            if df is not None and not df.empty:
                dfs.append(df)

        # If no handler returned data, return an empty list
        if not dfs:
            return []

        # Merge all DataFrames into one
        # ignore_index=True avoids duplicated indexes
        merged = pd.concat(dfs, ignore_index=True)

        # Remove duplicate categories (as required by UML)
        merged = merged.drop_duplicates()

        # Convert each row into a Category object
        return [
            Category(
                id=row["categoryId"],        # category identifier
                name=row["categoryName"]     # category name
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAllAreas(self) -> list:
        """
        UML: getAllAreas() : list[Area]

        Returns all areas from Scimago,
        with no repetitions.
        """

        dfs = []

        # Call getAllAreas on every CategoryQueryHandler
        for handler in self.categoryQuery:
            df = handler.getAllAreas()

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        # Merge and remove duplicates
        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        # Convert rows into Area objects
        return [
            Area(
                id=row["areaId"],          # area identifier
                name=row["areaName"]       # area name
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """
        UML: getCategoriesWithQuartile(quartiles : set[string]) : list[Category]

        Returns categories belonging to the specified quartiles.
        If the input set is empty, all quartiles are considered.
        """

        dfs = []

        # Delegate the filtering logic to the handlers
        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

#METHODSSS
    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear()
        return True
    
    def cleanCategoryHandlers(self) -> bool: #River
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear()
        return True
    
    def addJournalHandler(self, handler) -> bool: #Claudia
        self.journalQuery.append(handler)
        return True
    
    def addCategoryHandler(self, handler) -> bool: #River
        """Add a Category Query Handler to the list"""
        self.categoryQuery.append(handler)
        return True
    
    def getEntityById(self, id: str): #Claudia
        """Get an entity by its ID"""
        # Implementation needed
        return None

    #Polina methods from here
    def getAllJournals(self) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._collect_journals(df, journal_map)
        return list(journal_map.values())

    def getJournalsWithTitle(self, partialTitle: str) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithTitle(partialTitle)
            self._collect_journals(df, journal_map)
        return list(journal_map.values())

    def getJournalsPublishedBy(self, partialName: str) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsPublishedBy(partialName)
            self._collect_journals(df, journal_map)
        return list(journal_map.values())

    def getJournalsWithLicense(self, licenses: set) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._collect_journals(df, journal_map)
        return list(journal_map.values())

    def getJournalsWithAPC(self) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithAPC()
            self._collect_journals(df, journal_map)
        return list(journal_map.values())

    def getJournalsWithDOAJSeal(self) -> List[Journal]:
        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithDOAJSeal()
            self._collect_journals(df, journal_map)
        return list(journal_map.values())
        
    #Fahmida methods from heree
    def getAllCategories(self) -> list:
        """Get all categories from all category handlers"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getAllCategories())
        return categories
    
    def getAllAreas(self) -> list:
        """Get all areas from all category handlers"""
        areas = []
        for handler in self.categoryQuery:
            areas.extend(handler.getAllAreas())
        return areas
    
    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """Get categories with specified quartiles"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getCategoriesWithQuartile(quartiles))
        return categories
    
    def getCategoriesAssignedToAreas(self, area_ids: set) -> list:
        """Get categories assigned to specified areas"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getCategoriesAssignedToAreas(area_ids))
        return categories
    
    def getAreasAssignedToCategories(self, category_ids: set) -> list:
        """Get areas assigned to specified categories"""
        areas = []
        for handler in self.categoryQuery:
            areas.extend(handler.getAreasAssignedToCategories(category_ids))
        return areas

#Subclass --> FullQueryEngine(BasicQueryEngine) 