#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine: #Fahmida
    def __init__(self):
        self.journalQuery = []     # list of JournalQueryHandler --> journalQuery is an attribute that represents data, not classes! -> i'm storing objects created from that class
        self.categoryQuery = []    # list of CategoryQueryHandler --> # empty list of CategoryQueryHandler objects

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