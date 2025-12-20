class QueryHandler(Handler):
 """
 Base class for executing queries against a database.
 """
 
def __init__(self, dbPathOrUrl: str):
    super().__init__(dbPathOrUrl)

def getById(self, entity_id: str) -> pd.DataFrame:    
     raise NotImplementedError(
         "getById() must be implemented in subclasses"
     )