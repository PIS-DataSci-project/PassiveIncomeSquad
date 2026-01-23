import pandas as pd
from Entities import Journal, Category, Area


class FullQueryEngine:
    def __init__(self):
        self.journalQuery = []    # List of JournalQueryHandler objects
        self.categoryQuery = []   # List of CategoryQueryHandler objects
    
    def addJournalHandler(self, handler) -> bool:
        self.journalQuery.append(handler)
        return True
    
    def addCategoryHandler(self, handler) -> bool:
        self.categoryQuery.append(handler)
        return True
    
    def cleanJournalHandlers(self) -> bool:
        self.journalQuery = []
        return True
    
    def cleanCategoryHandlers(self) -> bool:
        self.categoryQuery = []
        return True
    
    def getEntityById(self, entity_id: str):
        """
        Search for entity by ID in all databases.
        Returns: Journal, Category, Area, or None
        """
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
                
                # Get categories for this journal from category handlers
                category_dfs = []
                for handler in self.categoryQuery:
                    cat_df = handler.getCategoriesForJournal(entity_id)
                    if cat_df is not None and not cat_df.empty:
                        category_dfs.append(cat_df)
                
                categories = []
                if category_dfs:
                    cat_merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates()
                    if 'category_id' in cat_merged.columns:
                        categories = [str(cat_id).strip() for cat_id in cat_merged['category_id'].dropna() if str(cat_id).strip()]
                
                # Get areas for this journal from category handlers
                area_dfs = []
                for handler in self.categoryQuery:
                    area_df = handler.getAreasForJournal(entity_id)
                    if area_df is not None and not area_df.empty:
                        area_dfs.append(area_df)
                
                areas = []
                if area_dfs:
                    area_merged = pd.concat(area_dfs, ignore_index=True).drop_duplicates()
                    if 'area' in area_merged.columns:
                        areas = [str(area).strip() for area in area_merged['area'].dropna() if str(area).strip()]
                    elif 'areas' in area_merged.columns:
                        areas = [str(area).strip() for area in area_merged['areas'].dropna() if str(area).strip()]
                
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
                    identifier=str(row.get('identifier', '')),
                    title=str(row.get('title', '')),
                    language=str(row.get('language', '')),
                    publisher=str(row.get('publisher', '')),
                    seal=seal,
                    license=str(row.get('license', '')),
                    apc=apc,
                    hasCategory=categories,
                    hasArea=areas
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
                
                # Check if it has quartile column (means it's a Category)
                if 'quartile' in merged.columns and pd.notna(row.get('quartile')):
                    return Category(
                        identifier=str(row.get('identifier', '')),
                        name=str(row.get('name', '')),
                        quartile=str(row.get('quartile', '')),
                        hasArea=[]
                    )
                else:
                    return Area(
                        identifier=str(row.get('identifier', '')),
                        name=str(row.get('name', ''))
                    )
        
        # 3. Not found in any database
        return None