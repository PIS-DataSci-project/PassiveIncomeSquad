import unittest

import pandas as pd

from BasicQueryEngine import BasicQueryEngine


class MockJournalQueryHandler:
    def __init__(self, rows):
        self.rows = rows

    def _frame(self):
        return pd.DataFrame(self.rows)

    def getById(self, entity_id):
        return self._frame()

    def getJournalsWithTitle(self, partial_title):
        return self._frame()

    def getJournalsPublishedBy(self, partial_name):
        return self._frame()

    def getJournalsWithLicense(self, licenses):
        return self._frame()

    def getJournalsWithAPC(self):
        return self._frame()

    def getJournalsWithDOAJSeal(self):
        return self._frame()


class BasicQueryEngineTests(unittest.TestCase):
    def test_get_journals_with_title_returns_journal_objects(self):
        engine = BasicQueryEngine()
        engine.addJournalHandler(
            MockJournalQueryHandler(
                [
                    {
                        "identifier": "1234-5678; 8765-4321",
                        "title": "Test Journal",
                        "language": "English",
                        "publisher": "Test Pub",
                        "seal": True,
                        "license": "CC BY",
                        "apc": False,
                    }
                ]
            )
        )

        journals = engine.getJournalsWithTitle("Test")

        self.assertEqual(1, len(journals))
        journal = journals[0]
        self.assertEqual(["1234-5678", "8765-4321"], journal.getIds())
        self.assertEqual("Test Journal", journal.getTitle())
        self.assertEqual("Test Pub", journal.getPublisher())
        self.assertTrue(journal.hasDOAJSeal())
        self.assertEqual("CC BY", journal.getLicense())
        self.assertFalse(journal.hasAPC())


if __name__ == "__main__":
    unittest.main()


