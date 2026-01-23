import pandas as pd
from typing import List, Dict
from impl import IdentifiableEntity, Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler  
from QueryEngine import BasicQueryEngine

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
                
                # Extract identifier - try different column names and validate
                id_value = None
                if 'identifier' in row and pd.notna(row['identifier']) and str(row['identifier']).strip():
                    id_value = str(row['identifier']).strip()
                elif 'identifiers' in row and pd.notna(row['identifiers']) and str(row['identifiers']).strip():
                    id_value = str(row['identifiers']).strip()
                
                # Use validated ID or fallback to search ID
                id_list = [id_value] if id_value else [str(id)]
                
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
                
                # Check if it's a Category (has quartile column with data)
                # Note: CategoryQueryHandler searches the categories table which only has categories
                # Areas cannot be found by ID in the current schema
                if 'quartile' in row and pd.notna(row['quartile']) and str(row['quartile']).strip():
                    # Create and return Category object
                    # Extract identifier from correct column - ensure it's a valid string
                    id_value = None
                    if 'category_id' in row and pd.notna(row['category_id']) and str(row['category_id']).strip():
                        id_value = str(row['category_id']).strip()
                    elif 'identifiers' in row and pd.notna(row['identifiers']) and str(row['identifiers']).strip():
                        id_value = str(row['identifiers']).strip()
                    
                    # Use validated ID or fallback to search ID
                    id_list = [id_value] if id_value else [str(id)]
                    
                    category = Category(
                        identifiers=id_list,
                        quartile=str(row['quartile']).strip()
                    )
                    return category
        
        # No entity found with this ID
        return None
    
# --------------------------------

rel_path = "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"

cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(rel_path)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

# Finally, create a advanced mashup object for asking
# about data
que = BasicQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

result_q3 = que.getEntityById("Medicine")
result_q4 = que.getEntityById("2532-8816")

print(result_q3)
print(result_q4)