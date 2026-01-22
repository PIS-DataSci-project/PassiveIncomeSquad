# We need pandas to merge DataFrames returned by the handlers
import pandas as pd

# Optional but good practice: type hints
# from typing import List, Set

# Superclass --> BasicQueryEngine(object)
class BasicQueryEngine:
    """
    This class corresponds to the UML class BasicQueryEngine.
    It coordinates multiple QueryHandler objects and combines their results.
    """

    def __init__(self):
        # UML: journalQuery : JournalQueryHandler [0..*]
        # In Python, [0..*] is represented by a list
        # This list will store OBJECTS of type JournalQueryHandler
        self.journalQuery = []

        # UML: categoryQuery : CategoryQueryHandler [0..*]
        # This list will store OBJECTS of type CategoryQueryHandler
        self.categoryQuery = []

    # ---------------------------------------------------------
    # CATEGORY-RELATED METHODS (assigned to Fahmida)
    # ---------------------------------------------------------

    def getAllCategories(self) -> list:
        """
        UML: getAllCategories() : list[Category]

        Returns all categories from Scimago Journal Rank,
        with no repetitions.
        """

        # This list will collect DataFrames returned by each handler
        dfs = []

        # Call the same method on ALL CategoryQueryHandler objects
        for handler in self.categoryQuery:
            # Each handler queries its own data source
            df = handler.getAllCategories()

            # We only keep non-empty results
            if df is not None and not df.empty:
                dfs.append(df)

        # If no handler returned data, return an empty list
        if not dfs:
            return []

        # Merge all DataFrames into one
        # ignore_index=True avoids duplicated indexes
        merged = pd.concat(dfs, ignore_index=True)

        # Remove duplicate categories (as required by UML)
        merged = merged.drop_duplicates()

        # Convert each row into a Category object
        return [
            Category(
                id=row["categoryId"],        # category identifier
                name=row["categoryName"]     # category name
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAllAreas(self) -> list:
        """
        UML: getAllAreas() : list[Area]

        Returns all areas from Scimago,
        with no repetitions.
        """

        dfs = []

        # Call getAllAreas on every CategoryQueryHandler
        for handler in self.categoryQuery:
            df = handler.getAllAreas()

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        # Merge and remove duplicates
        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        # Convert rows into Area objects
        return [
            Area(
                id=row["areaId"],          # area identifier
                name=row["areaName"]       # area name
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """
        UML: getCategoriesWithQuartile(quartiles : set[string]) : list[Category]

        Returns categories belonging to the specified quartiles.
        If the input set is empty, all quartiles are considered.
        """

        dfs = []

        # Delegate the filtering logic to the handlers
        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []
