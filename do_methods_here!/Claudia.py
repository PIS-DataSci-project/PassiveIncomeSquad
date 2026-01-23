import pandas as pd
from typing import List, Dict
from impl import IdentifiableEntity, Journal, Category, Area
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
                journal_map = Journal( 
                    identifiers=[journal_id.strip() for journal_id in row['identifiers'].split(',') if journal_id.strip()], # splitting the identifiers string into a list and 
                    title=row['title'], # getting the title from the row
                    language=[lang.strip() for lang in row['language'].split(',') if lang.strip()], # splitting the language string into a list # could add .strip() to remove extra spaces
                    seal=row['seal'] if 'seal' in row else False,
                    license=row['license'], 
                    apc=row['apc'] if 'apc' in row else False,
                    publisher=row['publisher'] if 'publisher' in row else None,
                )
                return journal_map # could have not created the variable and return the Journal object directly
        
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
                # Take the first row and construct a Category object
                row = merged.iloc[0]
                category = Category(
                    identifiers=[category_id.strip() for category_id in row['identifiers'].split(',') if category_id.strip()],
                    quartile=row['quartile']
                )
                return category
        
        # If not found in categories, search for areas in category handlers
        area_dfs = list() # creating a list to store dataframes from area handlers
        for handler in self.categoryQuery: # iterating through each CategoryQueryHandler object (areas are handled by category handlers)
            df = handler.getById(id) # calling getById method on each handler to get a dataframe for the given id
            if df is not None and len(df) > 0: # checking if the dataframe is valid and not empty
                area_dfs.append(df) # adding the valid dataframe to the list
        
        # Merge and remove duplicates from area results
        if area_dfs:
            merged = pd.concat(area_dfs, ignore_index=True).drop_duplicates() # concatenating all dataframes in the list into a single dataframe and removing duplicates
            if len(merged) > 0: # checking if the merged dataframe is not empty
                # Take the first row and construct an Area object
                row = merged.iloc[0]
                area = Area(
                    identifiers=[area_id.strip() for area_id in row['identifiers'].split(',') if area_id.strip()]
                )
                return area
        
        # No entity found with this ID
        return None