#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler
import sqlite3

# type hints
from typing import List, Set

#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine:
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
    
    def cleanCategoryHandlers(self) -> bool: #River
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear()
        return True
    
    def addJournalHandler(self, handler) -> bool: #River
        self.journalQuery.append(handler)
        return True
    
    def addCategoryHandler(self, handler) -> bool: #Claudia
        """Add a Category Query Handler to the list"""
        self.categoryQuery.append(handler)
        return True
    
    def getEntityById(self, id: str): #Claudia 
        """Get an entity (Journal or Category) by its ID"""
        # First, search through all journal handlers
        journal_dfs = [] 
        for handler in self.journalQuery:
            df = handler.getById(id)  
            if df is not None and not df.empty:
                journal_dfs.append(df)
        
        # Merge and remove duplicates from journal results
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).sort_values(by=list(pd.concat(journal_dfs).columns)).drop_duplicates()
            if not merged.empty:
                # Take the first row and construct a Journal object
                row = merged.iloc[0]
                journal = Journal(
                    identifiers=[id],
                    title=row.get('title', ''),
                    language=row.get('language', ''),
                    seal=row.get('seal', False),
                    license=row.get('license', ''),
                    apc=row.get('apc', False),
                    publisher=row.get('publisher', None)
                )
                return journal
        
        # If not found in journals, search through category handlers
        category_dfs = []
        for handler in self.categoryQuery:
            df = handler.getById(id)
            if df is not None and not df.empty:
                category_dfs.append(df)
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).sort_values(by=list(pd.concat(category_dfs).columns)).drop_duplicates()
            if not merged.empty:
                # Take the first row and construct a Category object
                row = merged.iloc[0]
                category = Category(
                    identifiers=[id],
                    quartile=row.get('quartile', '')
                )
                return category
        
        # No entity found with this ID
        return None
       

    #Polina methods from here
    def getJournalsWithTitle(self, partialTitle: str) -> List[Journal]:
        """Get journals with matching title"""
        journal_map: Dict[str, Journal] = {}
        
        try:
            for handler in self._journalQuery:
                df = handler.getJournalsWithTitle(partialTitle)
                self._collect_journals(df, journal_map)
        
                return list(journal_map.values())
        
        except Exception as e:
             print(f"Error while fetching journals with title '{partialTitle}': {e}")
             return []
    
    def getJournalsWithTitle(self, partialTitle: str) -> list:
        """Get journals matching the partial title"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getJournalsWithTitle(partialTitle))
        return journals
    
    def getJournalsPublishedBy(self, partialName: str) -> list:
        """Get journals published by a specific publisher"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getJournalsPublishedBy(partialName))
        return journals
    
    def getJournalsWithLicense(self, licenses: set) -> list:
        """Get journals with specified licenses"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getJournalsWithLicense(licenses))
        return journals
    
    def getJournalsWithAPC(self) -> list:
        """Get journals with Article Processing Charges"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getJournalsWithAPC())
        return journals
    
    def getJournalsWithDOAJSeal(self) -> list:
        """Get journals with DOAJ seal"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getJournalsWithDOAJSeal())
        return journals
        
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

#Subclass --> FullQueryEngine(BasicQueryEngine) 