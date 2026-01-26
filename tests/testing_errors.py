"""
Comprehensive Test Suite for PassiveIncomeSquad Implementation
Tests all classes and their required methods from impl.py
"""

import unittest
import sys
import os
import pandas as pd
import json
import tempfile
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from impl import (
    IdentifiableEntity, Journal, Category, Area,
    Handler, UploadHandler, JournalUploadHandler, CategoryUploadHandler,
    QueryHandler, JournalQueryHandler, CategoryQueryHandler,
    BasicQueryEngine, FullQueryEngine
)


class TestEntities(unittest.TestCase):
    """Test all Entity classes and their required methods"""
    
    def test_identifiable_entity_creation(self):
        """IdentifiableEntity should store and return identifiers"""
        entity = IdentifiableEntity(["id1", "id2", "id3"])
        ids = entity.getIds()
        self.assertEqual(len(ids), 3)
        self.assertIn("id1", ids)
        self.assertIn("id2", ids)
        self.assertIn("id3", ids)
        print("✓ IdentifiableEntity.getIds() works correctly")
    
    def test_journal_creation_and_methods(self):
        """Journal must have all required attributes and methods"""
        journal = Journal(
            identifiers=["1234-5678", "8765-4321"],
            title="Test Journal",
            language=["English", "Spanish"],
            seal=True,
            license="CC BY",
            apc=True,
            publisher="Test Publisher"
        )
        
        # Test required methods
        self.assertEqual(journal.getTitle(), "Test Journal")
        self.assertEqual(journal.getPublisher(), "Test Publisher")
        self.assertTrue(journal.hasPublisher("Test Publisher"))
        self.assertFalse(journal.hasPublisher("Other Publisher"))
        
        langs = journal.getLanguage()
        self.assertIn("English", langs)
        self.assertIn("Spanish", langs)
        
        self.assertTrue(journal.hasDOAJSeal())
        self.assertEqual(journal.getLicense(), "CC BY")
        self.assertTrue(journal.hasAPC())
        
        # Test identifiers from parent class
        ids = journal.getIds()
        self.assertEqual(len(ids), 2)
        
        print("✓ Journal class has all required methods")
        print("  - getTitle()")
        print("  - getPublisher()")
        print("  - hasPublisher()")
        print("  - getLanguage()")
        print("  - hasDOAJSeal()")
        print("  - getLicense()")
        print("  - hasAPC()")
        print("  - getIds()")
    
    def test_journal_with_categories_and_areas(self):
        """Journal should handle categories and areas"""
        cat = Category(["AI"], "Q1")
        area = Area(["Computer Science"])
        
        journal = Journal(
            identifiers=["1234-5678"],
            title="AI Journal",
            language=["English"],
            seal=False,
            license="CC BY",
            apc=False,
            categories=[cat],
            areas=[area]
        )
        
        self.assertEqual(len(journal.getCategories()), 1)
        self.assertTrue(journal.hasCategory(cat))
        self.assertEqual(len(journal.getAreas()), 1)
        self.assertTrue(journal.hasArea(area))
        
        print("✓ Journal handles categories and areas")
        print("  - getCategories()")
        print("  - hasCategory()")
        print("  - getAreas()")
        print("  - hasArea()")
    
    def test_category_creation(self):
        """Category must have quartile and identifiers"""
        category = Category(["Artificial Intelligence"], "Q1")
        
        self.assertEqual(category.getQuartile(), "Q1")
        ids = category.getIds()
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], "Artificial Intelligence")
        
        print("✓ Category class has required methods")
        print("  - getQuartile()")
        print("  - getIds()")
    
    def test_area_creation(self):
        """Area must inherit from IdentifiableEntity"""
        area = Area(["Medicine", "Computer Science"])
        ids = area.getIds()
        self.assertEqual(len(ids), 2)
        self.assertIn("Medicine", ids)
        
        print("✓ Area class inherits getIds() from IdentifiableEntity")


class TestHandlers(unittest.TestCase):
    """Test Handler classes and their required methods"""
    
    def test_handler_base_class(self):
        """Handler must have getDbPathOrUrl and setDbPathOrUrl"""
        handler = Handler()
        
        # Initially empty
        self.assertEqual(handler.getDbPathOrUrl(), "")
        
        # Set valid path
        result = handler.setDbPathOrUrl("test.db")
        self.assertTrue(result)
        self.assertEqual(handler.getDbPathOrUrl(), "test.db")
        
        # Set invalid path (empty)
        result = handler.setDbPathOrUrl("")
        self.assertFalse(result)
        
        print("✓ Handler class has required methods")
        print("  - getDbPathOrUrl()")
        print("  - setDbPathOrUrl()")
    
    def test_upload_handler_inheritance(self):
        """UploadHandler must inherit from Handler and have pushDataToDb"""
        handler = UploadHandler()
        
        # Should have Handler methods
        self.assertTrue(hasattr(handler, 'getDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'setDbPathOrUrl'))
        
        # Should have pushDataToDb (abstract)
        self.assertTrue(hasattr(handler, 'pushDataToDb'))
        
        print("✓ UploadHandler inherits from Handler")
        print("  - Has pushDataToDb() method")
    
    def test_journal_upload_handler_methods(self):
        """JournalUploadHandler must have required methods"""
        handler = JournalUploadHandler()
        
        # Check all required methods exist
        self.assertTrue(hasattr(handler, 'setDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'getDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'pushDataToDb'))
        self.assertTrue(hasattr(handler, 'createGraph'))
        self.assertTrue(hasattr(handler, 'serializeToTTL'))
        
        print("✓ JournalUploadHandler has required methods")
        print("  - setDbPathOrUrl()")
        print("  - getDbPathOrUrl()")
        print("  - pushDataToDb()")
        print("  - createGraph()")
        print("  - serializeToTTL()")
    
    def test_category_upload_handler_methods(self):
        """CategoryUploadHandler must have required methods"""
        handler = CategoryUploadHandler()
        
        # Check all required methods exist
        self.assertTrue(hasattr(handler, 'setDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'getDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'pushDataToDb'))
        
        print("✓ CategoryUploadHandler has required methods")
        print("  - setDbPathOrUrl()")
        print("  - getDbPathOrUrl()")
        print("  - pushDataToDb()")


class TestQueryHandlers(unittest.TestCase):
    """Test QueryHandler classes and their required methods"""
    
    def test_query_handler_inheritance(self):
        """QueryHandler must inherit from Handler"""
        handler = QueryHandler()
        
        # Should have Handler methods
        self.assertTrue(hasattr(handler, 'getDbPathOrUrl'))
        self.assertTrue(hasattr(handler, 'setDbPathOrUrl'))
        
        print("✓ QueryHandler inherits from Handler")
    
    def test_journal_query_handler_methods(self):
        """JournalQueryHandler must have all required query methods"""
        handler = JournalQueryHandler()
        
        required_methods = [
            'getDbPathOrUrl',
            'setDbPathOrUrl',
            'getAllJournals',
            'getJournalsWithTitle',
            'getJournalsPublishedBy',
            'getJournalsWithLicense',
            'getJournalsWithAPC',
            'getJournalsWithDOAJSeal',
            'getById'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(handler, method), 
                          f"JournalQueryHandler missing method: {method}")
        
        print("✓ JournalQueryHandler has all required methods")
        for method in required_methods:
            print(f"  - {method}()")
    
    def test_category_query_handler_methods(self):
        """CategoryQueryHandler must have all required query methods"""
        handler = CategoryQueryHandler()
        
        required_methods = [
            'getDbPathOrUrl',
            'setDbPathOrUrl',
            'getAllCategories',
            'getAllAreas',
            'getCategoriesWithQuartile',
            'getCategoriesAssignedToAreas',
            'getAreasAssignedToCategories',
            'getCategoriesByJournalId',
            'getAreasByJournalId'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(handler, method), 
                          f"CategoryQueryHandler missing method: {method}")
        
        print("✓ CategoryQueryHandler has all required methods")
        for method in required_methods:
            print(f"  - {method}()")


class TestBasicQueryEngine(unittest.TestCase):
    """Test BasicQueryEngine and its required methods"""
    
    def test_basic_query_engine_initialization(self):
        """BasicQueryEngine should initialize empty handler lists"""
        engine = BasicQueryEngine()
        
        self.assertTrue(hasattr(engine, 'journalQuery'))
        self.assertTrue(hasattr(engine, 'categoryQuery'))
        self.assertIsInstance(engine.journalQuery, list)
        self.assertIsInstance(engine.categoryQuery, list)
        
        print("✓ BasicQueryEngine initializes correctly")
        print("  - Has journalQuery list")
        print("  - Has categoryQuery list")
    
    def test_basic_query_engine_handler_management(self):
        """BasicQueryEngine must manage handlers"""
        engine = BasicQueryEngine()
        
        # Test adding handlers
        self.assertTrue(hasattr(engine, 'addJournalHandler'))
        self.assertTrue(hasattr(engine, 'addCategoryHandler'))
        
        # Test cleaning handlers
        self.assertTrue(hasattr(engine, 'cleanJournalHandlers'))
        self.assertTrue(hasattr(engine, 'cleanCategoryHandlers'))
        
        print("✓ BasicQueryEngine has handler management methods")
        print("  - addJournalHandler()")
        print("  - addCategoryHandler()")
        print("  - cleanJournalHandlers()")
        print("  - cleanCategoryHandlers()")
    
    def test_basic_query_engine_query_methods(self):
        """BasicQueryEngine must have all required query methods"""
        engine = BasicQueryEngine()
        
        required_methods = [
            # Journal-related
            'getAllJournals',
            'getJournalsWithTitle',
            'getJournalsPublishedBy',
            'getJournalsWithLicense',
            'getJournalsWithAPC',
            'getJournalsWithDOAJSeal',
            # Category-related
            'getAllCategories',
            'getAllAreas',
            'getCategoriesWithQuartile',
            'getCategoriesAssignedToAreas',
            'getAreasAssignedToCategories',
            # Entity lookup
            'getEntityById',
            # Helper methods
            'getCategoriesByJournalId',
            'getAreasByJournalId'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(engine, method), 
                          f"BasicQueryEngine missing method: {method}")
        
        print("✓ BasicQueryEngine has all required query methods")
        for method in required_methods:
            print(f"  - {method}()")


class TestFullQueryEngine(unittest.TestCase):
    """Test FullQueryEngine and its required methods"""
    
    def test_full_query_engine_inheritance(self):
        """FullQueryEngine should inherit from BasicQueryEngine"""
        engine = FullQueryEngine()
        
        # Should have BasicQueryEngine methods
        self.assertTrue(hasattr(engine, 'addJournalHandler'))
        self.assertTrue(hasattr(engine, 'addCategoryHandler'))
        self.assertTrue(hasattr(engine, 'getAllJournals'))
        self.assertTrue(hasattr(engine, 'getEntityById'))
        
        print("✓ FullQueryEngine inherits from BasicQueryEngine")
    
    def test_full_query_engine_mashup_methods(self):
        """FullQueryEngine must have mashup query methods"""
        engine = FullQueryEngine()
        
        mashup_methods = [
            'getJournalsInCategoriesWithQuartile',
            'getJournalsInAreasWithLicense',
            'getDiamondJournalsInAreasAndCategoriesWithQuartile'
        ]
        
        for method in mashup_methods:
            self.assertTrue(hasattr(engine, method), 
                          f"FullQueryEngine missing mashup method: {method}")
        
        print("✓ FullQueryEngine has mashup query methods")
        for method in mashup_methods:
            print(f"  - {method}()")
    
    def test_full_query_engine_helper_methods(self):
        """FullQueryEngine must have helper methods"""
        engine = FullQueryEngine()
        
        # Check for helper method
        self.assertTrue(hasattr(engine, '_parse_list_field'))
        
        print("✓ FullQueryEngine has helper methods")
        print("  - _parse_list_field()")


class TestReturnTypes(unittest.TestCase):
    """Test that methods return correct types"""
    
    def test_handler_return_types(self):
        """Handler methods should return correct types"""
        handler = Handler()
        
        # setDbPathOrUrl should return bool
        result = handler.setDbPathOrUrl("test.db")
        self.assertIsInstance(result, bool)
        
        # getDbPathOrUrl should return string
        result = handler.getDbPathOrUrl()
        self.assertIsInstance(result, str)
        
        print("✓ Handler methods return correct types")
        print("  - setDbPathOrUrl() returns bool")
        print("  - getDbPathOrUrl() returns str")
    
    def test_entity_return_types(self):
        """Entity methods should return correct types"""
        journal = Journal(
            identifiers=["1234"],
            title="Test",
            language=["English"],
            seal=True,
            license="CC BY",
            apc=False
        )
        
        # Test return types
        self.assertIsInstance(journal.getIds(), list)
        self.assertIsInstance(journal.getTitle(), str)
        self.assertIsInstance(journal.getPublisher(), str)
        self.assertIsInstance(journal.hasPublisher("Test"), bool)
        self.assertIsInstance(journal.getLanguage(), list)
        self.assertIsInstance(journal.hasDOAJSeal(), bool)
        self.assertIsInstance(journal.getLicense(), str)
        self.assertIsInstance(journal.hasAPC(), bool)
        self.assertIsInstance(journal.getCategories(), list)
        self.assertIsInstance(journal.getAreas(), list)
        
        print("✓ Entity methods return correct types")
        print("  - getIds() returns list")
        print("  - getTitle() returns str")
        print("  - hasDOAJSeal() returns bool")
        print("  - getCategories() returns list")


class TestDatasetCounts(unittest.TestCase):
    """Test that datasets contain expected number of records"""
    
    @classmethod
    def setUpClass(cls):
        """Count records in raw data files"""
        # Count journals in CSV
        cls.csv_path = "data/doaj.csv"
        cls.json_path = "data/scimago.json"
        
        try:
            df = pd.read_csv(cls.csv_path)
            cls.expected_journal_count = len(df)
        except Exception as e:
            print(f"Warning: Could not read {cls.csv_path}: {e}")
            cls.expected_journal_count = None
        
        # Count categories and areas in JSON
        try:
            with open(cls.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cls.expected_json_records = len(data)
            
            # Count unique categories
            categories = set()
            areas = set()
            
            for record in data:
                cats = record.get('categories', [])
                if isinstance(cats, list):
                    for cat in cats:
                        if isinstance(cat, dict) and 'id' in cat:
                            categories.add(cat['id'])
                
                record_areas = record.get('areas')
                if isinstance(record_areas, list):
                    areas.update(record_areas)
            
            cls.expected_category_count = len(categories)
            cls.expected_area_count = len(areas)
            
        except Exception as e:
            print(f"Warning: Could not read {cls.json_path}: {e}")
            cls.expected_json_records = None
            cls.expected_category_count = None
            cls.expected_area_count = None
    
    def test_doaj_csv_journal_count(self):
        """Verify doaj.csv contains 21,307 journals"""
        if self.expected_journal_count is None:
            self.skipTest("Could not read doaj.csv")
        
        self.assertEqual(self.expected_journal_count, 21307, 
                        f"Expected 21,307 journals in doaj.csv, found {self.expected_journal_count}")
        
        print(f"✓ doaj.csv contains {self.expected_journal_count:,} journals")
    
    def test_scimago_json_record_count(self):
        """Verify scimago.json contains 28,175 records"""
        if self.expected_json_records is None:
            self.skipTest("Could not read scimago.json")
        
        self.assertEqual(self.expected_json_records, 28175,
                        f"Expected 28,175 records in scimago.json, found {self.expected_json_records}")
        
        print(f"✓ scimago.json contains {self.expected_json_records:,} records")
    
    def test_scimago_json_category_count(self):
        """Verify scimago.json contains 310 unique categories"""
        if self.expected_category_count is None:
            self.skipTest("Could not read scimago.json")
        
        self.assertEqual(self.expected_category_count, 310,
                        f"Expected 310 unique categories in scimago.json, found {self.expected_category_count}")
        
        print(f"✓ scimago.json contains {self.expected_category_count} unique categories")
    
    def test_scimago_json_area_count(self):
        """Verify scimago.json contains 27 unique areas"""
        if self.expected_area_count is None:
            self.skipTest("Could not read scimago.json")
        
        self.assertEqual(self.expected_area_count, 27,
                        f"Expected 27 unique areas in scimago.json, found {self.expected_area_count}")
        
        print(f"✓ scimago.json contains {self.expected_area_count} unique areas")


class TestDataLoadingIntegration(unittest.TestCase):
    """Test that handlers correctly load data from files"""
    
    @classmethod
    def setUpClass(cls):
        """Set up temporary databases for testing"""
        cls.csv_path = "data/doaj.csv"
        cls.json_path = "data/scimago.json"
        
        # Create temporary SQLite database
        cls.temp_db = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
        cls.temp_db.close()
        cls.relational_db_path = cls.temp_db.name
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files"""
        try:
            os.unlink(cls.relational_db_path)
        except:
            pass
    
    def test_category_upload_loads_all_data(self):
        """Verify CategoryUploadHandler loads all categories from JSON"""
        if not os.path.exists(self.json_path):
            self.skipTest("scimago.json not found")
        
        # Upload data
        handler = CategoryUploadHandler()
        handler.setDbPathOrUrl(self.relational_db_path)
        result = handler.pushDataToDb(self.json_path)
        
        self.assertTrue(result, "pushDataToDb should return True")
        
        # Query to verify data was loaded
        conn = sqlite3.connect(self.relational_db_path)
        cur = conn.cursor()
        
        # Count unique categories
        cur.execute("SELECT COUNT(DISTINCT category_id) FROM categories")
        category_count = cur.fetchone()[0]
        
        # Count unique areas
        cur.execute("SELECT COUNT(DISTINCT areas) FROM categories WHERE areas IS NOT NULL")
        area_count = cur.fetchone()[0]
        
        conn.close()
        
        # Verify counts
        self.assertGreater(category_count, 0, "Should have loaded categories")
        self.assertEqual(category_count, 310, f"Should have 310 unique categories, found {category_count}")
        
        print(f"✓ CategoryUploadHandler loaded {category_count} unique categories")
        print(f"✓ CategoryUploadHandler loaded data with {area_count} unique area entries")
    
    def test_category_query_handler_returns_all_data(self):
        """Verify CategoryQueryHandler can retrieve all loaded data"""
        if not os.path.exists(self.json_path):
            self.skipTest("scimago.json not found")
        
        # Upload data first
        upload_handler = CategoryUploadHandler()
        upload_handler.setDbPathOrUrl(self.relational_db_path)
        upload_handler.pushDataToDb(self.json_path)
        
        # Query data
        query_handler = CategoryQueryHandler()
        query_handler.setDbPathOrUrl(self.relational_db_path)
        
        # Get all categories
        all_categories = query_handler.getAllCategories()
        self.assertIsNotNone(all_categories, "getAllCategories should not return None")
        self.assertFalse(all_categories.empty, "getAllCategories should return non-empty DataFrame")
        
        unique_categories = all_categories['category_id'].nunique()
        self.assertEqual(unique_categories, 310, 
                        f"Should return 310 unique categories, found {unique_categories}")
        
        # Get all areas
        all_areas = query_handler.getAllAreas()
        self.assertIsNotNone(all_areas, "getAllAreas should not return None")
        self.assertFalse(all_areas.empty, "getAllAreas should return non-empty DataFrame")
        
        unique_areas = all_areas['area'].nunique()
        self.assertEqual(unique_areas, 27, 
                        f"Should return 27 unique areas, found {unique_areas}")
        
        print(f"✓ CategoryQueryHandler.getAllCategories() returns {unique_categories} unique categories")
        print(f"✓ CategoryQueryHandler.getAllAreas() returns {unique_areas} unique areas")


def run_all_tests():
    """Run all test suites and provide summary"""
    print("=" * 80)
    print("IMPLEMENTATION VALIDATION TEST SUITE")
    print("Testing all required classes and methods from impl.py")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEntities))
    suite.addTests(loader.loadTestsFromTestCase(TestHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicQueryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestFullQueryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestReturnTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetCounts))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoadingIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED - Implementation meets requirements!")
    else:
        print("✗ SOME TESTS FAILED - Check implementation")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
