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

    def _add_journals_from_df(
            self,
            df: pd.DataFrame,
            journal_map: dict[str, Journal]
    ) -> None:
        if df is None or df.empty:
            return

        for _, row in df.iterrows():
            journal_id = row["journal"]
            if journal_id and journal_id not in journal_map:
                journal_map[journal_id] = Journal(
                    identifiers=[journal_id.strip() for journal_id in row['identifiers'].split(',') if journal_id.strip()], # splitting the identifiers string into a list and 
                    title=row['title'], # getting the title from the row
                    language=[lang.strip() for lang in row['language'].split(',') if lang.strip()], # splitting the language string into a list # could add .strip() to remove extra spaces
                    seal=row['seal'] if 'seal' in row else False,
                    license=row['license'], 
                    apc=row['apc'] if 'apc' in row else False,
                    publisher=row['publisher'] if 'publisher' in row else None,
                    )

    def getAllJournals(self) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())
    
    def getJournalsWithTitle(self, partialTitle: str) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getJournalsWithTitle(partialTitle)
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())

    
    def getJournalsPublishedBy(self, partialName: str) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getJournalsPublishedBy(partialName)
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())

    
    def getJournalsWithLicense(self, licenses: set[str]) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())

    
    def getJournalsWithAPC(self) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery: 
            df = handler.getJournalsWithAPC()
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())

    
    def getJournalsWithDOAJSeal(self) -> list[Journal]:
        journal_map: dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getJournalsWithDOAJSeal()
            self._add_journals_from_df(df, journal_map)

        return list(journal_map.values())



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
