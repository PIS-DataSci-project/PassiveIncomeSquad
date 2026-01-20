# Copyright (c) 2023, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
import unittest
from os import sep
from pandas import DataFrame
from Handlers import *
from Entities import *

# REMEMBER: before launching the tests, please run the Blazegraph instance!

class TestProjectBasic(unittest.TestCase):

    # The paths of the files used in the test should change depending on what you want to use
    # and the folder where they are. Instead, for the graph database, the URL to talk with
    # the SPARQL endpoint must be updated depending on how you launch it - currently, it is
    # specified the URL introduced during the course, which is the one used for a standard
    # launch of the database.
    journal = "data" + sep + "doaj.csv"
    category = "data" + sep + "scimago.json"
    relational = "." + sep + "relational.db"
    graph = "http://127.0.0.1:9999/blazegraph/sparql"
    
    def test_01_JournalUploadHandler(self):
        u = JournalUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.graph))
        self.assertEqual(u.getDbPathOrUrl(), self.graph)
        self.assertTrue(u.pushDataToDb(self.journal))
        print("✓ test_01_JournalUploadHandler passed")

    def test_02_CategoryUploadHandler(self):
        u = CategoryUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.relational))
        self.assertEqual(u.getDbPathOrUrl(), self.relational)
        self.assertTrue(u.pushDataToDb(self.category))
        print("✓ test_02_CategoryUploadHandler passed")
    
    def test_03_JournalQueryHandler(self):
        q = JournalQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.graph))
        self.assertEqual(q.getDbPathOrUrl(), self.graph)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllJournals(), DataFrame)
        self.assertIsInstance(q.getJournalsWithTitle("just_a_test"), DataFrame)
        self.assertIsInstance(q.getJournalsPublishedBy("just_a_test"), DataFrame)
        self.assertIsInstance(q.getJournalsWithLicense({"just_a_test"}), DataFrame)
        self.assertIsInstance(q.getJournalsWithAPC(), DataFrame)
        self.assertIsInstance(q.getJournalsWithDOAJSeal(), DataFrame)
        print("✓ test_03_JournalQueryHandler passed")
    
    def test_04_ProcessDataQueryHandler(self):
        q = CategoryQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.relational))
        self.assertEqual(q.getDbPathOrUrl(), self.relational)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllCategories(), DataFrame)
        self.assertIsInstance(q.getAllAreas(), DataFrame)
        self.assertIsInstance(q.getCategoriesWithQuartile({"just_a_test"}), DataFrame)
        self.assertIsInstance(q.getCategoriesAssignedToAreas({"just_a_test"}), DataFrame)
        self.assertIsInstance(q.getAreasAssignedToCategories({"just_a_test"}), DataFrame)
        print("✓ test_04_ProcessDataQueryHandler passed")