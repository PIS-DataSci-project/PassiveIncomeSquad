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
    
# --------------------------------
cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl("relational.db")

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl("http://127.0.0.1:9999/blazegraph/sparql")

que = BasicQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

# First let's test what the handlers return directly
print("Testing handler.getById() directly:")
test_id = "Medicine"
print(f"\nTesting with ID: {test_id}")

# Test journal handler directly
jou_result = jou_qh.getById(test_id)
print(f"Journal handler result: {type(jou_result)}, len={len(jou_result) if jou_result is not None else 'None'}")
if jou_result is not None and len(jou_result) > 0:
    print(f"Columns: {jou_result.columns.tolist()}")
    print(f"Data:\n{jou_result}")

# Test category handler with a category ID
cat_test_id = "Medicine"  # Try a numeric category ID
print(f"\nTesting category with ID: {cat_test_id}")
cat_result = cat_qh.getById(cat_test_id)
print(f"Category handler result: {type(cat_result)}, len={len(cat_result) if cat_result is not None else 'None'}")
if cat_result is not None and len(cat_result) > 0:
    print(f"Columns: {cat_result.columns.tolist()}")
    print(f"Data:\n{cat_result}")

print("\n" + "="*60)
print("Now testing getEntityById method:")
print("="*60)

result_q4 = que.getEntityById(test_id)
print(f"Result for {test_id}: {result_q4}")
if result_q4:
    print(f"Type: {type(result_q4).__name__}")

result_cat = que.getEntityById(cat_test_id)
print(f"\nResult for {cat_test_id}: {result_cat}")
if result_cat:
    print(f"Type: {type(result_cat).__name__}")