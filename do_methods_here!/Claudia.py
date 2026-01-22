import pandas as pd
from impl import * 

#------------------------------------------------
#Subclass of BasicQueryEngine

class BasicQueryEngine: 
    
    def getEntityById(self, id: str) -> IdentifiableEntity:
        dfs = []
        # First, search through all journal handlers
        for handler in self.journalQuery:
            df = handler.getById(id)
            
            if df is not None and not df.empty:
                # We found a journal matching this ID
                # Take the first row (should be only one)
                row = df.iloc[0]
                
                # Construct a Journal object with the data
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
        for handler in self.categoryQuery:
            df = handler.getById(id)
            
            if df is not None and not df.empty:
                # We found a category matching this ID
                row = df.iloc[0]
                
                # Construct a Category object with the data
                category = Category(
                    identifiers=[id],
                    quartile=row.get('quartile', '')
                )
                return category
        
        # No entity found with this ID
        return None
    