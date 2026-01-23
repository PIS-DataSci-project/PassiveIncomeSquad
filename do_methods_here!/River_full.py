import pandas as pd 
from typing import List, Dict
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler
import sqlite3

# type hints
from typing import List, Set

class FullQueryEngine(BasicQueryEngine):  # Claudia
    """
    Extends BasicQueryEngine with mashup queries across data sources.
    Returns Python entity objects (Journal, Category, Area).
    """

    def _extract_identifier_set(self, df: pd.DataFrame) -> set[str]:
        if df is None or df.empty:
            return set()
        identifiers = set()
        for value in df.get("identifiers", []):
            for identifier in self._parse_identifiers(value):
                identifiers.add(identifier)
        return identifiers

    def _coerce_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        text = str(value).strip().lower()
        return text in {"true", "1", "yes"}

    def _add_journals_matching_identifiers(
        self,
        df: pd.DataFrame,
        identifiers: set[str],
        journal_map: dict[str, Journal],
        require_no_apc: bool = False,
    ) -> None:
        if df is None or df.empty:
            return
        if not identifiers:
            return
        for _, row in df.iterrows():
            row_identifiers = self._parse_identifiers(row.get("identifier"))
            if not row_identifiers:
                continue
            if not any(identifier in identifiers for identifier in row_identifiers):
                continue
            if require_no_apc and self._coerce_bool(row.get("apc")):
                continue
            primary_id = row_identifiers[0]
            if primary_id not in journal_map:
                journal_map[primary_id] = Journal(
                    identifiers=row_identifiers,
                    title=row.get("title", ""),
                    language=row.get("language", ""),
                    seal=row.get("seal", False),
                    license=row.get("license", ""),
                    apc=row.get("apc", False),
                    publisher=row.get("publisher", None),
                )

    def getJournalsInCategoriesWithQuartile(
        self,
        category_ids: set[str],
        quartiles: set[str],
    ) -> list[Journal]:
        if not category_ids or not quartiles:
            return []
        identifiers: set[str] = set()
        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is None or df.empty:
                continue
            df = df[df["category_id"].isin(category_ids)]
            identifiers |= self._extract_identifier_set(df)
        journal_map: dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers(df, identifiers, journal_map)
        return list(journal_map.values())  # River

    def getJournalsInAreasWithLicense(      
        self,
        area_ids: set[str],
        licenses: set[str],
    ) -> list[Journal]:
        if not area_ids or not licenses:
            return []
        identifiers: set[str] = set()
        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            identifiers |= self._extract_identifier_set(df)
        journal_map: dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._add_journals_matching_identifiers(df, identifiers, journal_map)
        return list(journal_map.values())

    def getDiamondJournalsInAreasAndCategoriesWithQuartile(
        self,
        area_ids: set[str],
        category_ids: set[str],
        quartiles: set[str],
    ) -> list[Journal]:
        if not area_ids or not category_ids or not quartiles:
            return []
        identifiers: set[str] = set()
        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            if df is None or df.empty:
                continue
            df = df[df["category_id"].isin(category_ids)]
            df = df[df["quartile"].isin(quartiles)]
            identifiers |= self._extract_identifier_set(df)
        journal_map: dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers(
                df,
                identifiers,
                journal_map,
                require_no_apc=True,
            )
        return list(journal_map.values())