import pandas as pd 
import json 
import sqlite3
from rdflib import Graph, URIRef, RDF, Literal, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from Entities import *


class Handler:
    """Base handler for database connection management"""
    def __init__(self):
        self.dbPathOrUrl = ""

    def getdbPathOrUrl(self):
        """Get the current database path or URL"""
        return self.dbPathOrUrl

    def setdbPathOrUrl(self, dbPathOrUrl):
        """Set and validate database path or URL"""
        if dbPathOrUrl and dbPathOrUrl.strip():
            self.dbPathOrUrl = dbPathOrUrl
            return True
        else:
            return False 

        
class UploadHandler(Handler):
    """Abstract handler for data upload operations"""
    def __init__(self):
        super().__init__()

    def pushDataToDb(self, path):
        """Upload data to database - must be implemented by subclasses"""
        pass

    
class JournalUploadHandler(UploadHandler): # CLAUDIA
    """Uploads journal data from CSV to RDF triplestore"""
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)
    
    def _normalize_bool(self, value):
        """Convert Yes/No text values to boolean (case-insensitive)"""
        if isinstance(value, str):
            return value.strip().lower() == "yes"
        return bool(value)
    
    def createGraph(self, path):
        """Create RDF graph from CSV file"""
        # URI Definitions
        baseUrl = "https://github.com/PassiveIncomeSquad/PIS-DataSci-project"
        # Journal type and properties
        Journal = URIRef("https://schema.org/Periodical") 
        title = URIRef("https://schema.org/title")
        identifier = URIRef("http://schema.org/identifier") 
        language = URIRef("http://schema.org/inLanguage")
        publisher = URIRef("http://schema.org/publishedBy") 
        seal = URIRef("https://schema.org/award")
        license = URIRef("https://schema.org/license")
        apc = URIRef("https://schema.org/processingFee")
        # Create RDF graph
        g = Graph()
        journals = pd.read_csv(path, keep_default_na=False,
            dtype={
                "Journal title": "string",
                "Journal ISSN (print version)": "string",  
                "Journal EISSN (online version)": "string",
                "Languages in which the journal accepts manuscripts": "string",
                "Publisher": "string",
                "DOAJ Seal": "string",
                "Journal license": "string", 
                "APC": "string"
            })
        for idx, row in journals.iterrows():
            localId = "journal-" + str(idx)
            subj = URIRef(baseUrl + "/" + localId)
            g.add((subj, RDF.type, Journal))
            g.add((subj, title, Literal(row["Journal title"])))
            # Combine ISSN and EISSN
            issn = row["Journal ISSN (print version)"].strip()
            eissn = row["Journal EISSN (online version)"].strip()
            issn_and_eissn = "; ".join(filter(None, [issn, eissn]))
            if issn_and_eissn:
                g.add((subj, identifier, Literal(issn_and_eissn)))
            g.add((subj, language, Literal(row["Languages in which the journal accepts manuscripts"])))
            g.add((subj, publisher, Literal(row["Publisher"])))
            g.add((subj, license, Literal(row["Journal license"])))
            # Normalize boolean values
            seal_bool = self._normalize_bool(row["DOAJ Seal"])
            apc_bool = self._normalize_bool(row["APC"])
            g.add((subj, seal, Literal(seal_bool, datatype=XSD.boolean)))
            g.add((subj, apc, Literal(apc_bool, datatype=XSD.boolean)))
        return g
    
    def pushDataToDb(self, path):
        g = self.createGraph(path)
        store = SPARQLUpdateStore()
        store.open((self.dbPathOrUrl, self.dbPathOrUrl))
        # Upload all triples to SPARQL store
        for triple in g.triples((None, None, None)):
            store.add(triple)
        store.close()

class QueryHandler(Handler): #Polina
  """Base class for executing queries against a database."""
 
  def __init__(self, dbPathOrUrl: str):
      super().__init__(dbPathOrUrl)

  def getById(self, entity_id: str) -> pd.DataFrame:    
     raise NotImplementedError(
         "getById() must be implemented in subclasses"
     )

class CategoryUploadHandler(UploadHandler): # River
    """Uploads category data from Scimago JSON into a relational DB."""
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)

    def pushDataToDb(self, path):
        if not path.endswith(".json"):
            return False

        with open(path, "r", encoding="utf-8") as file_handle:
            scimago_data = json.load(file_handle)

        conn = sqlite3.connect(self.dbPathOrUrl)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS journals (
                journal_id TEXT PRIMARY KEY
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                quartile TEXT NOT NULL,
                UNIQUE(category_name, quartile)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS areas (
                area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT NOT NULL UNIQUE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_categories (
                journal_id TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (journal_id, category_id),
                FOREIGN KEY (journal_id) REFERENCES journals(journal_id),
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_areas (
                journal_id TEXT NOT NULL,
                area_id INTEGER NOT NULL,
                PRIMARY KEY (journal_id, area_id),
                FOREIGN KEY (journal_id) REFERENCES journals(journal_id),
                FOREIGN KEY (area_id) REFERENCES areas(area_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS category_areas (
                category_id INTEGER NOT NULL,
                area_id INTEGER NOT NULL,
                PRIMARY KEY (category_id, area_id),
                FOREIGN KEY (category_id) REFERENCES categories(category_id),
                FOREIGN KEY (area_id) REFERENCES areas(area_id)
            )
            """
        )

        for item in scimago_data:
            identifiers = item.get("identifiers", [])
            categories = item.get("categories", [])
            areas = item.get("areas", [])

            area_ids = []
            for area_name in areas:
                if area_name:
                    cursor.execute(
                        "INSERT OR IGNORE INTO areas (area_name) VALUES (?)",
                        (area_name,),
                    )
                    cursor.execute(
                        "SELECT area_id FROM areas WHERE area_name = ?",
                        (area_name,),
                    )
                    area_ids.append(cursor.fetchone()[0])

            category_ids = []
            for category in categories:
                category_name = category.get("id")
                quartile = category.get("quartile")
                if category_name and quartile:
                    cursor.execute(
                        "INSERT OR IGNORE INTO categories (category_name, quartile) VALUES (?, ?)",
                        (category_name, quartile),
                    )
                    cursor.execute(
                        "SELECT category_id FROM categories WHERE category_name = ? AND quartile = ?",
                        (category_name, quartile),
                    )
                    category_id = cursor.fetchone()[0]
                    category_ids.append(category_id)
                    for area_id in area_ids:
                        cursor.execute(
                            "INSERT OR IGNORE INTO category_areas (category_id, area_id) VALUES (?, ?)",
                            (category_id, area_id),
                        )

            for identifier in identifiers:
                if not identifier:
                    continue
                cursor.execute(
                    "INSERT OR IGNORE INTO journals (journal_id) VALUES (?)",
                    (identifier,),
                )
                for category_id in category_ids:
                    cursor.execute(
                        "INSERT OR IGNORE INTO journal_categories (journal_id, category_id) VALUES (?, ?)",
                        (identifier, category_id),
                    )
                for area_id in area_ids:
                    cursor.execute(
                        "INSERT OR IGNORE INTO journal_areas (journal_id, area_id) VALUES (?, ?)",
                        (identifier, area_id),
                    )

        conn.commit()
        conn.close()
        return True
