#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
from typing import List, Dict
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler
import sqlite3

# type hints
from typing import List, Set

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
    
    def getEntityById(self, id: str): #Claudia 
        """Get an entity (Journal or Category) by its ID"""
        # First, search through all journal handlers
        journal_dfs = list() # creating a list to store dataframes from journal handlers
        for handler in self.journalQuery: # iterating through each JournalQueryHandler object in the journalQuery list
            df = handler.getById(id) # calling getById method on each handler to get a dataframe for the given id
            if df is not None and len(df) > 0: # checking if the dataframe is valid and not empty
                journal_dfs.append(df) # adding the valid dataframe to the list
        
        # Merge and remove duplicates from journal results
        if journal_dfs: 
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates() # concatenating all dataframes in the list into a single dataframe and removing duplicates
            if len(merged) > 0: # checking if the merged dataframe is not empty
                # Take the first row and construct a Journal object
                row = merged.iloc[0] # getting the first row of the merged dataframe
                
                # Extract identifier - try different column names
                if 'identifier' in row:
                    id_list = [row['identifier']]
                elif 'identifiers' in row:
                    id_list = [row['identifiers']]
                else:
                    id_list = [id]
                
                # Extract language
                lang_str = row.get('language', '')
                if lang_str and isinstance(lang_str, str):
                    lang_list = [lang.strip() for lang in lang_str.split(';') if lang.strip()]
                else:
                    lang_list = []
                
                journal = Journal( 
                    identifiers=id_list,
                    title=row.get('title', ''),
                    language=lang_list,
                    seal=row.get('seal', False),
                    license=row.get('license', ''), 
                    apc=row.get('apc', False),
                    publisher=row.get('publisher', None),
                )
                return journal
        
        # If not found in journals, search through category handlers
        category_dfs = list() # creating a list to store dataframes from category handlers
        for handler in self.categoryQuery: # iterating through each CategoryQueryHandler object in the categoryQuery list
            df = handler.getById(id) # calling getById method on each handler to get a dataframe for the given id
            if df is not None and len(df) > 0: # checking if the dataframe is valid and not empty
                category_dfs.append(df) # adding the valid dataframe to the list
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates() # concatenating all dataframes in the list into a single dataframe and removing duplicates
            if len(merged) > 0: # checking if the merged dataframe is not empty
                # Take the first row and determine entity type
                row = merged.iloc[0]
                
                # Check if it's a Category (has quartile column with data) or Area (no quartile)
                if 'quartile' in row and pd.notna(row['quartile']) and row['quartile']:
                    # Create and return Category object
                    # Extract identifier from correct column
                    if 'category_id' in row:
                        id_list = [row['category_id']]
                    elif 'identifiers' in row:
                        id_list = [row['identifiers']]
                    else:
                        id_list = [id]
                    
                    category = Category(
                        identifiers=id_list,
                        quartile=str(row['quartile'])
                    )
                    return category
                else:
                    # Create and return Area object
                    if 'areas' in row:
                        id_list = [row['areas']]
                    elif 'identifiers' in row:
                        id_list = [row['identifiers']]
                    else:
                        id_list = [id]
                    
                    area = Area(
                        identifiers=id_list
                    )
                    return area
        
        # No entity found with this ID
        return None
       

    #Polina methods from here
    def getAllJournals(self) -> list:
        """Получить все журналы"""
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

    def getJournalsWithTitle(self, partialTitle: str) -> list:
        """Найти журналы по названию"""
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

    def getJournalsPublishedBy(self, partialName: str) -> list:
        """Найти журналы по издателю"""
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

    def getJournalsWithLicense(self, licenses: set) -> list:
        """Найти журналы с лицензиями"""
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

    def getJournalsWithAPC(self) -> list:
        """Найти журналы с APC"""
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

    def getJournalsWithDOAJSeal(self) -> list:
        """Найти журналы с DOAJ Seal"""
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

#Subclass --> FullQueryEngine(BasicQueryEngine) 