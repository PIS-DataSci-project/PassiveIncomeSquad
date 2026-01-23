#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
import pandas as pd 
from typing import List, Dict
from Entities import Journal
from impl import JournalQueryHandler, CategoryQueryHandler

# Superclass --> BasicQueryEngine(object)
class BasicQueryEngine:
    """
    UML class: BasicQueryEngine
    Coordinates multiple QueryHandler objects and combines their results.
    """

    def __init__(self):
        # UML: journalQuery : JournalQueryHandler [0..*]
        self.journalQuery = []

        # UML: categoryQuery : CategoryQueryHandler [0..*]
        self.categoryQuery = []

    #Polina methods from here

    def getAllJournals(self) -> list:
        """Получить все журналы"""
        all_dfs = [handler.getAllJournals() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    def getJournalsWithTitle(self, partialTitle: str) -> list:
        """Найти журналы по названию"""
        all_dfs = [handler.getJournalsWithTitle(partialTitle) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    def getJournalsPublishedBy(self, partialName: str) -> list:
        """Найти журналы по издателю"""
        all_dfs = [handler.getJournalsPublishedBy(partialName) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    def getJournalsWithLicense(self, licenses: set) -> list:
        """Найти журналы с лицензиями"""
        all_dfs = [handler.getJournalsWithLicense(licenses) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()

        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    def getJournalsWithAPC(self) -> list:
        """Найти журналы с APC"""
        all_dfs = [handler.getJournalsWithAPC() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    def getJournalsWithDOAJSeal(self) -> list:
        """Найти журналы с DOAJ Seal"""
        all_dfs = [handler.getJournalsWithDOAJSeal() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
    
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]



#Subclass --> FullQueryEngine(BasicQueryEngine) 

#testing 
def test_get_all_journals_returns_journal_list():
    handler = MagicMock()

    handler.getAllJournals.return_value = pd.DataFrame([
        {
            "journal": "j1",
            "title": "Test Journal",
            "language": "en",
            "seal": True,
            "license": "CC-BY",
            "apc": True,
            "publisher": "Test Publisher"
        }
    ])

    engine = BasicQueryEngine()
    engine.journalQuery = [handler]

    result = engine.getAllJournals()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Journal)
    assert result[0].title == "Test Journal"
