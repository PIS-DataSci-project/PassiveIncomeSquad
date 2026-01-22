#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
from Entities import *
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler

#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine: #Fahmida
    
    def __init__(self):
        self.journalQuery = []     # list of JournalQueryHandler --> journalQuery is an attribute that represents data, not classes! -> i'm storing objects created from that class
        self.categoryQuery = []    # list of CategoryQueryHandler --> # empty list of CategoryQueryHandler objects

    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear() # remove all elements from the list
        return True # indicate success
    
    def cleanCategoryHandlers(self) -> bool: #Claudia
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear() 
        return True
    
    def addJournalHandler(self, handler) -> bool: #River
        self.journalQuery.append(handler) # 
        return True 
    
    def addCategoryHandler(self, handler) -> bool: #River
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
    def getAllJournals(self) -> list:
        """Get all journals from all journal handlers"""
        journals = []
        for handler in self.journalQuery:
            journals.extend(handler.getAllJournals())
        return journals
    
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
        
    #Fahmida methods from here
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