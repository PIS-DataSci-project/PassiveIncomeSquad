# We need pandas to merge DataFrames returned by the handlers
import pandas as pd

# Optional but good practice: type hints
from typing import List, Set

#for tests
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler


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

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                id=row["categoryId"],
                name=row["categoryName"]
            )
            for _, row in merged.iterrows()
        ]



    # ---------------------------------------------------------

    def getCategoriesAssignedToAreas(self, area_ids: set) -> list:
        """
        UML: getCategoriesAssignedToAreas(area_ids : set[string]) : list[Category]

        Returns categories assigned to the specified areas.
        If the input set is empty, all areas are considered.
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                id=row["categoryId"],
                name=row["categoryName"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAreasAssignedToCategories(self, category_ids: set) -> list:
        """
        UML: getAreasAssignedToCategories(category_ids : set[string]) : list[Area]

        Returns areas assigned to the specified categories.
        If the input set is empty, all categories are considered.
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getAreasAssignedToCategories(category_ids)

            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Area(
                id=row["areaId"],
                name=row["areaName"]
            )
            for _, row in merged.iterrows()
        ]

#test1 (runs correctly!!! = constructor is correct!):
engine = BasicQueryEngine()

#test2 (correct output!! = [] is correct!)
print(engine.getAllCategories())
#Why?
#self.categoryQuery is empty
#dfs stays empty
#method returns []
#If you get [] → logic is correct for empty case, which is required by UML.

#test3 (creates a fake handler - simulates scimago data - and adds it to the engine --> should return small dataframe)
class FakeCategoryQueryHandler:
    def getAllCategories(self):
        return pd.DataFrame([
            {"categoryId": "C1", "categoryName": "Computer Science"},
            {"categoryId": "C2", "categoryName": "Mathematics"}
        ])

    def getAllAreas(self):
        return pd.DataFrame([
            {"areaId": "A1", "areaName": "Engineering"}
        ])

    def getCategoriesWithQuartile(self, quartiles):
        return self.getAllCategories()

    def getCategoriesAssignedToAreas(self, area_ids):
        return self.getAllCategories()

    def getAreasAssignedToCategories(self, category_ids):
        return self.getAllAreas()
#plugging into the engine
engine = BasicQueryEngine()
engine.categoryQuery.append(FakeCategoryQueryHandler())
#testing each method
categories = engine.getAllCategories()
areas = engine.getAllAreas()

print(categories)
print(areas)

