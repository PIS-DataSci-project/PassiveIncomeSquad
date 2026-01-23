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
                journal = Journal( 
                    identifiers=[journal_id.strip() for journal_id in row['identifiers'].split(',') if journal_id.strip()], # splitting the identifiers string into a list and 
                    title=row['title'], # getting the title from the row
                    language=[lang.strip() for lang in row['language'].split(',') if lang.strip()], # splitting the language string into a list # could add .strip() to remove extra spaces
                    seal=row['seal'] if 'seal' in row else False,
                    license=row['license'], 
                    apc=row['apc'] if 'apc' in row else False,
                    publisher=row['publisher'] if 'publisher' in row else None,
                )
                return journal # could have not created the variable and return the Journal object directly
        
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
                row = merged.iloc[0] # getting the first row of the merged dataframe
                
                # Check if it's a Category (has quartile column with data) or Area (no quartile)
                if 'quartile' in row and row['quartile']:
                    # Create and return Category object
                    category = Category(
                        identifiers=[cat_id.strip() for cat_id in row['identifiers'].split(',') if cat_id.strip()],
                        quartile=row.get('quartile', '')
                    )
                    return category
                else:
                    # Create and return Area object
                    area = Area(
                        identifiers=[area_id.strip() for area_id in row['identifiers'].split(',') if area_id.strip()]
                    )
                    return area
        
        # No entity found with this ID
        return None
    
# --------------------------------
que = BasicQueryEngine()


result_q3 = que.getEntityById("Artificial Intelligence")
result_q4 = que.getEntityById("2532-8816")
result_q5 = que.getEntityById("NonExistentID")  # Testing with a non-existent ID
result_q6 = que.getEntityById("1234-5678")  # Testing with an ID that could belong to multiple entities
result_q7 = que.getEntityById("Medicine")  # Testing with a category ID