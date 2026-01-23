import pandas as pd
from typing import List, Dict
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler  

#------------------------------------------------
#Subclass of BasicQueryEngine

class BasicQueryEngine: #Fahmida
    
    def __init__(self):
        self.journalQuery = []     # list of JournalQueryHandler --> journalQuery is an attribute that represents data, not classes! -> i'm storing objects created from that class
        self.categoryQuery = []    # list of CategoryQueryHandler --> # empty list of CategoryQueryHandler objects

#METHODSSS
    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear() # remove all elements from the list
        return True # indicate success
    
    def cleanCategoryHandlers(self) -> bool: #Claudia
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear()
        return True
    
    def getEntityById(self, id: str): #Claudia 
        """Get an entity (Journal or Category) by its ID"""
        # First, search through all journal handlers
        journal_dfs = list()
        for handler in self.journalQuery:
            df = handler.getById(id)
            if df is not None and not df.empty:
                journal_dfs.append(df)
        
        # Merge and remove duplicates from journal results
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates()
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
        category_dfs = list()
        for handler in self.categoryQuery:
            df = handler.getById(id)
            if df is not None and not df.empty:
                category_dfs.append(df)
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates()
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