#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed Test File for FullQueryEngine Mashup Queries

This test file shows:
1. What data should be in your databases
2. What results you SHOULD get (expected)
3. What results you ACTUALLY get from your implementation
4. Comparison between expected and actual

Run this AFTER:
- Starting Blazegraph (http://127.0.0.1:9999/blazegraph/sparql)
- Uploading data to both databases
"""

import sys
from os import sep
from impl import JournalUploadHandler, CategoryUploadHandler
from impl import JournalQueryHandler, CategoryQueryHandler
from impl import FullQueryEngine, Journal, Category, Area

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"  {text}")


class TestFullQueryEngineWithExpectations:
    """Test class that shows expected vs actual results"""
    
    def __init__(self):
        self.journal_file = "data" + sep + "doaj.csv"
        self.category_file = "data" + sep + "scimago.json"
        self.relational_db = "." + sep + "relational.db"
        self.graph_endpoint = "http://192.168.1.183:9999/blazegraph/sparql"
        
        self.engine = None
        self.test_results = []
    
    def setup(self):
        """Setup databases and query engine"""
        print_header("SETUP: Uploading Data to Databases")
        
        try:
            # Upload to graph database
            print_info("Uploading journals to Blazegraph...")
            jou = JournalUploadHandler()
            jou.setDbPathOrUrl(self.graph_endpoint)
            if jou.pushDataToDb(self.journal_file):
                print_success("Journals uploaded to graph database")
            else:
                print_error("Failed to upload journals")
                return False
            
            # Upload to relational database
            print_info("Uploading categories to SQLite...")
            cat = CategoryUploadHandler()
            cat.setDbPathOrUrl(self.relational_db)
            if cat.pushDataToDb(self.category_file):
                print_success("Categories uploaded to relational database")
            else:
                print_error("Failed to upload categories")
                return False
            
            # Setup query handlers
            print_info("Setting up query handlers...")
            jou_qh = JournalQueryHandler()
            jou_qh.setDbPathOrUrl(self.graph_endpoint)
            
            cat_qh = CategoryQueryHandler()
            cat_qh.setDbPathOrUrl(self.relational_db)
            
            # Create query engine
            self.engine = FullQueryEngine()
            self.engine.addJournalHandler(jou_qh)
            self.engine.addCategoryHandler(cat_qh)
            
            print_success("Query engine ready")
            return True
            
        except Exception as e:
            print_error(f"Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_get_entity_by_id(self):
        """Test getEntityById with various entity types"""
        print_header("TEST 1: getEntityById()")
        
        test_cases = [
            {
                "id": "2532-8816",
                "type": "Journal (by ISSN)",
                "expected": "Should return a Journal object with title, license, etc.",
            },
            {
                "id": "Artificial Intelligence",
                "type": "Category (by name)",
                "expected": "Should return a Category object with quartile",
            },
            {
                "id": "Computer Science",
                "type": "Area (by name)",
                "expected": "Should return an Area object",
            },
            {
                "id": "nonexistent_id_12345",
                "type": "Non-existent",
                "expected": "Should return None",
            }
        ]
        
        for test in test_cases:
            print(f"\n{YELLOW}Testing ID: {test['id']} ({test['type']}){RESET}")
            print_info(f"Expected: {test['expected']}")
            
            try:
                result = self.engine.getEntityById(test['id'])
                
                if result is None:
                    print_info(f"Actual: None")
                    if "None" in test['expected']:
                        print_success("Result matches expectation")
                    else:
                        print_warning("Got None, but expected an entity")
                else:
                    result_type = type(result).__name__
                    print_info(f"Actual: {result_type} object")
                    
                    if isinstance(result, Journal):
                        print_info(f"  Title: {result.getTitle()}")
                        print_info(f"  IDs: {result.getIds()}")
                        print_info(f"  License: {result.getLicence()}")
                        print_success("Got Journal object" if "Journal" in test['expected'] else "Unexpected Journal object")
                    elif isinstance(result, Category):
                        print_info(f"  IDs: {result.getIds()}")
                        print_info(f"  Quartile: {result.getQuartile()}")
                        print_success("Got Category object" if "Category" in test['expected'] else "Unexpected Category object")
                    elif isinstance(result, Area):
                        print_info(f"  IDs: {result.getIds()}")
                        print_success("Got Area object" if "Area" in test['expected'] else "Unexpected Area object")
                        
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def test_journals_in_categories_with_quartile(self):
        """Test getJournalsInCategoriesWithQuartile"""
        print_header("TEST 2: getJournalsInCategoriesWithQuartile()")
        
        test_cases = [
            {
                "categories": {"Artificial Intelligence"},
                "quartiles": {"Q1"},
                "description": "Top AI journals (Q1 quartile)",
                "expected": "> 0 journals (should find Q1 AI journals)",
            },
            {
                "categories": {"Oncology", "Surgery"},
                "quartiles": {"Q1", "Q2"},
                "description": "Top medical journals in Oncology or Surgery",
                "expected": "> 0 journals (should find Q1/Q2 medical journals)",
            },
            {
                "categories": {"Nonexistent Category"},
                "quartiles": {"Q1"},
                "description": "Non-existent category",
                "expected": "0 journals (category doesn't exist)",
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{YELLOW}Test Case {i}: {test['description']}{RESET}")
            print_info(f"Categories: {test['categories']}")
            print_info(f"Quartiles: {test['quartiles']}")
            print_info(f"Expected: {test['expected']}")
            
            try:
                result = self.engine.getJournalsInCategoriesWithQuartile(
                    test['categories'], 
                    test['quartiles']
                )
                
                print_info(f"Actual: {len(result)} journals returned")
                
                if len(result) > 0:
                    print_success(f"Found {len(result)} journals")
                    print_info("Sample journals:")
                    for j in result[:3]:  # Show first 3
                        print_info(f"  - {j.getTitle()[:60]}... (IDs: {j.getIds()[0] if j.getIds() else 'N/A'})")
                    
                    if "> 0" in test['expected']:
                        print_success("Result matches expectation (found journals)")
                    else:
                        print_warning("Found journals but expected 0")
                else:
                    print_info("No journals found")
                    if "0 journals" in test['expected']:
                        print_success("Result matches expectation (0 journals)")
                    else:
                        print_error("Expected to find journals but got 0")
                        
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def test_journals_in_areas_with_license(self):
        """Test getJournalsInAreasWithLicense"""
        print_header("TEST 3: getJournalsInAreasWithLicense()")
        
        test_cases = [
            {
                "areas": {"Computer Science"},
                "licenses": {"CC BY"},
                "description": "Computer Science journals with CC BY license",
                "expected": "> 0 journals (should find open access CS journals)",
            },
            {
                "areas": {"Medicine", "Nursing"},
                "licenses": {"CC BY", "CC BY-NC"},
                "description": "Medical journals with Creative Commons licenses",
                "expected": "> 0 journals (should find open access medical journals)",
            },
            {
                "areas": {"Nonexistent Area"},
                "licenses": {"CC BY"},
                "description": "Non-existent area",
                "expected": "0 journals (area doesn't exist)",
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{YELLOW}Test Case {i}: {test['description']}{RESET}")
            print_info(f"Areas: {test['areas']}")
            print_info(f"Licenses: {test['licenses']}")
            print_info(f"Expected: {test['expected']}")
            
            try:
                result = self.engine.getJournalsInAreasWithLicense(
                    test['areas'], 
                    test['licenses']
                )
                
                print_info(f"Actual: {len(result)} journals returned")
                
                if len(result) > 0:
                    print_success(f"Found {len(result)} journals")
                    print_info("Sample journals:")
                    for j in result[:3]:  # Show first 3
                        print_info(f"  - {j.getTitle()[:60]}... (License: {j.getLicence()})")
                    
                    if "> 0" in test['expected']:
                        print_success("Result matches expectation (found journals)")
                    else:
                        print_warning("Found journals but expected 0")
                else:
                    print_info("No journals found")
                    if "0 journals" in test['expected']:
                        print_success("Result matches expectation (0 journals)")
                    else:
                        print_error("Expected to find journals but got 0")
                        
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def test_journals_in_areas_and_categories_with_quartile(self):
        """Test getJournalsInAreasAndCategoriesWithQuartile"""
        print_header("TEST 4: getJournalsInAreasAndCategoriesWithQuartile()")
        
        test_cases = [
            {
                "areas": {"Computer Science"},
                "categories": {"Artificial Intelligence"},
                "quartiles": {"Q1"},
                "description": "Top AI journals in Computer Science",
                "expected": "> 0 journals (should find Q1 AI journals in CS area)",
            },
            {
                "areas": {"Medicine"},
                "categories": {"Oncology", "Surgery"},
                "quartiles": {"Q1", "Q2"},
                "description": "Top medical journals",
                "expected": "> 0 journals (should find Q1/Q2 medical journals)",
            },
            {
                "areas": {"Computer Science"},
                "categories": {"Nonexistent Category"},
                "quartiles": {"Q1"},
                "description": "Non-existent category",
                "expected": "0 journals (category doesn't exist)",
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{YELLOW}Test Case {i}: {test['description']}{RESET}")
            print_info(f"Areas: {test['areas']}")
            print_info(f"Categories: {test['categories']}")
            print_info(f"Quartiles: {test['quartiles']}")
            print_info(f"Expected: {test['expected']}")
            
            try:
                result = self.engine.getJournalsInAreasAndCategoriesWithQuartile(
                    test['areas'],
                    test['categories'], 
                    test['quartiles']
                )
                
                print_info(f"Actual: {len(result)} journals returned")
                
                if len(result) > 0:
                    print_success(f"Found {len(result)} journals")
                    print_info("Sample journals:")
                    for j in result[:3]:  # Show first 3
                        print_info(f"  - {j.getTitle()[:60]}...")
                    
                    if "> 0" in test['expected']:
                        print_success("Result matches expectation (found journals)")
                    else:
                        print_warning("Found journals but expected 0")
                else:
                    print_info("No journals found")
                    if "0 journals" in test['expected']:
                        print_success("Result matches expectation (0 journals)")
                    else:
                        print_error("Expected to find journals but got 0")
                        
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def test_diamond_journals(self):
        """Test getDiamondJournalsInAreasAndCategoriesWithQuartile"""
        print_header("TEST 5: getDiamondJournalsInAreasAndCategoriesWithQuartile()")
        
        print_info("Diamond journals = journals with NO Article Processing Charge (APC)")
        
        test_cases = [
            {
                "areas": {"Computer Science"},
                "categories": {"Artificial Intelligence"},
                "quartiles": {"Q1"},
                "description": "Free-to-publish top AI journals",
                "expected": "> 0 journals (should find some Q1 AI journals without APC)",
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{YELLOW}Test Case {i}: {test['description']}{RESET}")
            print_info(f"Areas: {test['areas']}")
            print_info(f"Categories: {test['categories']}")
            print_info(f"Quartiles: {test['quartiles']}")
            print_info(f"Expected: {test['expected']}")
            
            try:
                # First get all journals in this area/category/quartile
                all_journals = self.engine.getJournalsInAreasAndCategoriesWithQuartile(
                    test['areas'],
                    test['categories'], 
                    test['quartiles']
                )
                
                # Then get diamond journals
                result = self.engine.getDiamondJournalsInAreasAndCategoriesWithQuartile(
                    test['areas'],
                    test['categories'], 
                    test['quartiles']
                )
                
                print_info(f"All journals: {len(all_journals)}")
                print_info(f"Diamond journals (no APC): {len(result)}")
                
                if len(result) > 0:
                    percentage = (len(result) / len(all_journals) * 100) if all_journals else 0
                    print_success(f"Found {len(result)} diamond journals ({percentage:.1f}% of total)")
                    print_info("Sample diamond journals:")
                    for j in result[:3]:  # Show first 3
                        print_info(f"  - {j.getTitle()[:60]}... (APC: {j.hasAPC()})")
                    
                    # Verify all have APC=False
                    all_diamond = all(not j.hasAPC() for j in result)
                    if all_diamond:
                        print_success("All journals correctly have APC=False")
                    else:
                        print_error("ERROR: Some journals have APC=True!")
                        
                    if "> 0" in test['expected']:
                        print_success("Result matches expectation (found journals)")
                    else:
                        print_warning("Found journals but expected 0")
                else:
                    print_info("No diamond journals found")
                    if "0 journals" in test['expected']:
                        print_success("Result matches expectation (0 journals)")
                    else:
                        print_warning("Expected to find journals but got 0")
                        print_info("This might be correct if all journals in this category have APC")
                        
            except Exception as e:
                print_error(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{BLUE}{'='*70}")
        print(f"  FULLQUERYENGINE COMPREHENSIVE TEST SUITE")
        print(f"  Testing Expected vs Actual Results")
        print(f"{'='*70}{RESET}\n")
        
        if not self.setup():
            print_error("Setup failed. Cannot continue with tests.")
            return
        
        # Run all tests
        self.test_get_entity_by_id()
        self.test_journals_in_categories_with_quartile()
        self.test_journals_in_areas_with_license()
        self.test_journals_in_areas_and_categories_with_quartile()
        self.test_diamond_journals()
        
        print_header("TEST SUITE COMPLETED")
        print_info("Review the results above to see if actual matches expected")


if __name__ == "__main__":
    print(f"\n{YELLOW}IMPORTANT:{RESET}")
    print("1. Make sure Blazegraph is running at http://127.0.0.1:9999/blazegraph/sparql")
    print("2. Make sure you have data/doaj.csv and data/scimago.json files")
    print("3. This will create/overwrite relational.db in current directory")
    
    input(f"\n{BLUE}Press Enter to continue...{RESET}\n")
    
    tester = TestFullQueryEngineWithExpectations()
    tester.run_all_tests()
