# We need pandas to merge DataFrames returned by the handlers
import pandas as pd

# Optional but good practice: type hints
from typing import List, Set

#for tests (the tests will work only if this file is in the root)
from impl import Journal, Category, Area
from impl import JournalQueryHandler, CategoryQueryHandler
import sqlite3


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

    # ---------------------------------------------------------
    # CATEGORY-RELATED METHODS (Fahmida)
    # ---------------------------------------------------------

    def getAllCategories(self) -> list:
        """
        UML: getAllCategories() : list[Category]
        Returns all categories with no repetitions.
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getAllCategories()
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAllAreas(self) -> list:
        """
        Returns all areas from Scimago, with no repetitions.
        """

        dfs = []

        # Call getAllAreas on every CategoryQueryHandler
        for handler in self.categoryQuery:
            df = handler.getAllAreas()  # returns column 'area'
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        # Merge and remove duplicates
        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        # Convert rows into Area objects
        return [
            Area(
                identifiers={row["area"]}  # <- this is the correct column
            )
            for _, row in merged.iterrows()
        ]


    # ---------------------------------------------------------

    def getCategoriesWithQuartile(self, quartiles: set) -> list:
        """
        UML: getCategoriesWithQuartile(quartiles : set[string]) : list[Category]
        """

        dfs = []

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is not None and not df.empty:
                dfs.append(df)

        if not dfs:
            return []

        merged = pd.concat(dfs, ignore_index=True).drop_duplicates()

        return [
            Category(
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getCategoriesAssignedToAreas(self, area_ids: set) -> list:
        """
        UML: getCategoriesAssignedToAreas(area_ids : set[string]) : list[Category]
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
                identifiers={row["category_id"]},
                quartile=row["quartile"]
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getAreasAssignedToCategories(self, category_ids: set) -> list:
        """
        UML: getAreasAssignedToCategories(category_ids : set[string]) : list[Area]
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
                identifiers={row["area"]}
            )
            for _, row in merged.iterrows()
        ]


#test0 (runs correctly!!! = constructor is correct!):
engine = BasicQueryEngine()

#test1 (correct output!! = [] is correct!)
print(engine.getAllCategories())
#Why?
#self.categoryQuery is empty
#dfs stays empty
#method returns []
#If you get [] → logic is correct for empty case, which is required by UML.

#test2 (passed testing engine logic: created the objects and called the method correctly):
engine = BasicQueryEngine()

handler = CategoryQueryHandler("relational.db") 
engine.categoryQuery.append(handler)

cats = engine.getAllCategories()
print(cats[0], type(cats[0]), cats[0].getQuartile())

areas = engine.getAllAreas()
print(areas[0], type(areas[0]))

print(cats[0], cats[0].getQuartile())
print(vars(areas[0]))  # shows all attributes of Area
# Expected: set with one area identifier

#test3 (testing engine without db --> worksssss):
import pandas as pd

# Mock classes for testing
class MockCategoryQueryHandler:
    """
    This mock simulates a CategoryQueryHandler without a database.
    Each method returns a small DataFrame to test BasicQueryEngine.
    """
    
    def getAllCategories(self):
        # Example DataFrame simulating categories
        return pd.DataFrame({
            "category_id": ["C1", "C2"],
            "quartile": ["Q1", "Q2"],
            "identifiers": ["C1", "C2"],        # instead of list
            "areas": ["Medicine", "Biology"]    # instead of list
        })
    
    def getAllAreas(self):
        # Example DataFrame simulating areas
        return pd.DataFrame({
            "area": ["Medicine", "Biology"]
        })
    
    def getCategoriesWithQuartile(self, quartiles):
        df = self.getAllCategories()
        if not quartiles:
            return df
        return df[df["quartile"].isin(quartiles)]
    
    def getCategoriesAssignedToAreas(self, area_ids):
        df = self.getAllCategories()
        if not area_ids:
            return df
        # Only keep categories where any area matches
        mask = df["areas"].apply(lambda x: any(area in area_ids for area in x))
        return df[mask]
    
    def getAreasAssignedToCategories(self, category_ids):
        df = self.getAllCategories()
        if not category_ids:
            return pd.DataFrame({"area": ["Medicine", "Biology"]})
        # Only keep areas for matching categories
        df = df[df["category_id"].isin(category_ids)]
        areas = [area for sublist in df["areas"] for area in sublist]
        return pd.DataFrame({"area": areas})

# Now test BasicQueryEngine with the mock
if __name__ == "__main__":
    engine = BasicQueryEngine()
    
    # Use the mock instead of a real handler
    mock_handler = MockCategoryQueryHandler()
    engine.categoryQuery.append(mock_handler)
    
    # Test all methods
    cats = engine.getAllCategories()
    print("All Categories:")
    for c in cats:
        print(c, type(c), c.getQuartile())
    
    areas = engine.getAllAreas()
    print("\nAll Areas:")
    for a in areas:
        print(a, type(a))
    
    q1_cats = engine.getCategoriesWithQuartile({"Q1"})
    print("\nCategories in Q1:")
    for c in q1_cats:
        print(c, c.getQuartile())
    
    medicine_cats = engine.getCategoriesAssignedToAreas({"Medicine"})
    print("\nCategories assigned to Medicine area:")
    for c in medicine_cats:
        print(c, c.getQuartile())
    
    cat_areas = engine.getAreasAssignedToCategories({"C1"})
    print("\nAreas assigned to category C1:")
    for a in cat_areas:
        print(a)
