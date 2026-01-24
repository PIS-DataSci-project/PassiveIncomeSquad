import pandas as pd
from typing import List, Dict
from impl import IdentifiableEntity, Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler  
from os import sep

#------------------------------------------------
#Subclass of BasicQueryEngine

class BasicQueryEngine: #Fahmida
    
    def __init__(self):
        self.journalQuery = []     # list of JournalQueryHandler
        self.categoryQuery = []    # list of CategoryQueryHandler

#METHODS
    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear()
        return True
    
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
    
    def getEntityById(self, entity_id: str):
        """
        Search for entity by ID in all databases.
        Returns: Journal or Category, or None
        """
        if not entity_id:
            return None
            
        # 1. Search in journal handlers (Blazegraph)
        journal_dfs = []
        for handler in self.journalQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                journal_dfs.append(result_df)
        
        # Merge and remove duplicates from journal results
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Parse identifiers from the identifier field (may contain multiple IDs separated by "; ")
                identifiers = []
                if 'identifier' in row and pd.notna(row['identifier']):
                    id_str = str(row['identifier'])
                    identifiers = [id.strip() for id in id_str.split(';') if id.strip()]
                
                # Parse languages from the language field (may contain multiple languages)
                languages = []
                if 'language' in row and pd.notna(row['language']):
                    lang_str = str(row['language'])
                    languages = [lang.strip() for lang in lang_str.split(',') if lang.strip()]
                
                # Get categories and areas using helper methods
                categories = GetCategoriesByJournalId(self, identifiers)
                areas = GetAreasByJournalId(self, identifiers)
                
                # Convert boolean strings to actual booleans
                seal = False
                if 'seal' in row:
                    if isinstance(row['seal'], str):
                        seal = row['seal'].lower() == 'true'
                    else:
                        seal = bool(row['seal'])
                
                apc = False
                if 'apc' in row:
                    if isinstance(row['apc'], str):
                        apc = row['apc'].lower() == 'true'
                    else:
                        apc = bool(row['apc'])
                
                return Journal(
                    identifiers=identifiers,
                    title=str(row.get('title', '')),
                    language=languages,
                    seal=seal,
                    license=str(row.get('license', '')),
                    apc=apc,
                    publisher=str(row.get('publisher', '')),
                    categories=categories,
                    areas=areas
                )
        
        # 2. Search in category handlers (SQLite)
        category_dfs = []
        for handler in self.categoryQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                category_dfs.append(result_df)
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Return Category
                identifiers = []
                if 'category_id' in row:
                    identifiers.append(str(row['category_id']))
                if 'identifiers' in row and pd.notna(row['identifiers']):
                    identifiers.append(str(row['identifiers']))
                
                return Category(
                    identifiers=list(set(identifiers)) if identifiers else [entity_id],
                    quartile=str(row.get('quartile', ''))
                )
        
        # 3. Not found in any database
        return None


# Helper function to print Journal details
def print_journal(journal):
    if journal is None:
        print("None")
        return
    
    print(f"Title: {journal.getTitle()}")
    print(f"IDs: {journal.getIds()}")
    print(f"Publisher: {journal.getPublisher()}")
    print(f"Languages: {journal.getLanguage()}")
    print(f"DOAJ Seal: {journal.hasDOAJSeal()}")
    print(f"License: {journal.getLicense()}")
    print(f"Has APC: {journal.hasAPC()}")
    print(f"Categories: {journal.getCategories()}")
    print(f"Areas: {journal.getAreas()}")

def GetCategoriesByJournalId(engine, journal_ids):
    """Get all Category objects for a journal. Prints category details."""
    if isinstance(journal_ids, str):
        journal_ids = [journal_ids]
    
    categories = []
    for handler in engine.categoryQuery:
        for journal_id in journal_ids:
            cat_df = handler.getById(journal_id)
            if cat_df is not None and not cat_df.empty:
                for _, row in cat_df.iterrows():
                    cat = Category(
                        identifiers=[str(row['category_id'])],
                        quartile=str(row.get('quartile', ''))
                    )
                    categories.append(cat)
                    # Print category details
                    if cat:
                        print(f"Category IDs: {cat.getIds()}")
                        print(f"Quartile: {cat.getQuartile()}")
    return categories

def GetAreasByJournalId(engine, journal_ids):
    """Get all Area objects for a journal. Prints area details."""
    if isinstance(journal_ids, str):
        journal_ids = [journal_ids]
    
    areas = []
    for handler in engine.categoryQuery:
        for journal_id in journal_ids:
            cat_df = handler.getById(journal_id)
            if cat_df is not None and not cat_df.empty:
                for _, row in cat_df.iterrows():
                    if 'areas' in row and pd.notna(row['areas']):
                        area_names = [a.strip() for a in str(row['areas']).split(',') if a.strip()]
                        for area_name in area_names:
                            area = Area(identifiers=[area_name])
                            areas.append(area)
                            # Print area details
                            if area:
                                print(f"Area IDs: {area.getIds()}")
    
    # Remove duplicates
    unique_areas = list({a.getIds()[0]: a for a in areas}.values())
    return unique_areas

# --------------------------------
journal = "data" + sep + "doaj.csv"
category = "data" + sep + "scimago.json"
relational = "." + sep + "relational.db"
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
    
jq = JournalQueryHandler()
jq.setDbPathOrUrl(grp_endpoint)
cq = CategoryQueryHandler()
cq.setDbPathOrUrl(relational)

fq = BasicQueryEngine()
fq.cleanJournalHandlers()
fq.cleanCategoryHandlers()
fq.addJournalHandler(jq)
fq.addCategoryHandler(cq)

result = fq.getEntityById("just_a_test")
if result is None:
    print("Test passed: getEntityById returned None for non-existent ID")
else:
    print("Test failed: expected None but got", result)
    
# USAGE 
cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl(relational)

jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

# Finally, create a advanced mashup object for asking
# about data
que = BasicQueryEngine()
que.addCategoryHandler(cat_qh)
que.addJournalHandler(jou_qh)

print("\nTesting various IDs:")
print("-" * 50)

result_q3 = que.getJournalPublishedBy("Salento")
print(result_q3)
result_q4 = que.getEntityById("2224-9281")
print_journal(result_q4)

if result_q3 and result_q4: 
    print("Both entities found successfully! ⭐")