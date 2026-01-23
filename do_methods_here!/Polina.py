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
            journal_id = row("journal")
            if journal_id and journal_id not in journal_map:
                journal_map[journal_id] = Journal(
                    identifiers=[journal_id],
                    title=row("title", ""),
                    language=row("language", ""),
                    seal=row("seal", False),
                    license=row("license", ""),
                    apc=row("apc", False),
                    publisher=row("publisher", None)
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
        
    #Fahmida methods from heree
    def getAllCategories(self) -> list:
        """Get all categories from all category handlers"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getAllCategories())
        return categories
    
    def getAllAreas(self) -> list:
        """Get all areas from all category handlers"""
        areas = []
        for handler in self.categoryQuery:
            areas.extend(handler.getAllAreas())
        return areas
    
    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """Get categories with specified quartiles"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getCategoriesWithQuartile(quartiles))
        return categories
    
    def getCategoriesAssignedToAreas(self, area_ids: set) -> list:
        """Get categories assigned to specified areas"""
        categories = []
        for handler in self.categoryQuery:
            categories.extend(handler.getCategoriesAssignedToAreas(area_ids))
        return categories
    
    def getAreasAssignedToCategories(self, category_ids: set) -> list:
        """Get areas assigned to specified categories"""
        areas = []
        for handler in self.categoryQuery:
            areas.extend(handler.getAreasAssignedToCategories(category_ids))
        return areas

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
