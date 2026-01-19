#ALL IMPORTS AT THE TOP OF THE FILE
#General imports
from Entities import *

#For Graph Database
from rdflib import Graph, URIRef, RDF, Literal, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

#For Relational Database
import json
import pandas as pd #for JournalUploadHandler
import sqlite3 #for CategoryQueryHandler

#---------------------------------------------------------------------------------------------
#superclass
class Handler(object):
    #Base handler for database connection management
    def __init__(self): # defines the constructor
        self.dbPathOrUrl = ""

    def getdbPathOrUrl(self):
        #Get the current database path or URL
        return self.dbPathOrUrl

    def setdbPathOrUrl(self, dbPathOrUrl):
        #Set and validate database path or URL
        if dbPathOrUrl and dbPathOrUrl.strip():
            self.dbPathOrUrl = dbPathOrUrl
            return True
        else:
            return False 

#subclass of Handler
class UploadHandler(Handler):
    #Abstract handler for data upload operations
    def __init__(self):
        super().__init__()

    def pushDataToDb(self, path):
        #Upload data to database - must be implemented by subclasses
        pass 

#subclass of UploadHandler
class JournalUploadHandler(UploadHandler): # CLAUDIA
    #Uploads journal data from CSV to RDF triplestore --> uploads data and tells me where it comes from
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)
    
    def _normalize_bool(self, value):
        #Convert Yes/No text values to boolean (case-insensitive)
        if isinstance(value, str):
            return value.strip().lower() == "yes"
        return bool(value)
    
    def createGraph(self, path):
        #Create RDF graph from CSV file
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
        endpoint = self.dbPathOrUrl 
        store.open((endpoint, endpoint))
        # Upload all triples to SPARQL store
        for triple in g.triples((None, None, None)):
            store.add(triple)
        store.close()
        return True # indicate success

#CategoryUploadHandler - River HEREE 
#JSON --> DataFrame --> DB
class CategoryUploadHandler(UploadHandler): # River
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)

    def pushDataToDb(self, path):
        if not isinstance(path, str) or not path.endswith(".json"):
            return False

        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)

        conn = sqlite3.connect(self.dbPathOrUrl)
        cur = conn.cursor()

        # Tables
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id TEXT,
                quartile TEXT,
                PRIMARY KEY (category_id, quartile)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS journals (
                journal_id TEXT PRIMARY KEY
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_categories (
                journal_id TEXT,
                category_id TEXT,
                quartile TEXT,
                PRIMARY KEY (journal_id, category_id, quartile)
            )
            """
        )

        for record in data:
            identifiers = record.get("identifiers", [])
            categories = record.get("categories", [])

            for category in categories:
                category_id = category.get("id")
                quartile = category.get("quartile")
                if not (category_id and quartile):
                    continue

                cur.execute(
                    "INSERT OR IGNORE INTO categories VALUES (?, ?)",
                    (category_id, quartile),
                )

                for issn in identifiers:
                    cur.execute(
                        "INSERT OR IGNORE INTO journals VALUES (?)",
                        (issn,),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO journal_categories VALUES (?, ?, ?)",
                        (issn, category_id, quartile),
                    )

        conn.commit()
        conn.close()
        return True


#---------------------------------------------------------------------------------------------

#subclass of Handler
class QueryHandler(Handler): #Polina
  #Base class for executing queries against a database.
 
  def __init__(self):
        super().__init__()

  def getById(self, entity_id: str) -> pd.DataFrame:    
     raise NotImplementedError(
         "getById() must be implemented in subclasses"
     )

#JournalQueryHandler - Polina HERE

#CategoryQueryHandler
# Subclass of QueryHandler - Fahmy  HERE--> i don't open file or normalize json here, i just query the DB. NO PANDAS LOADING HERE!
class CategoryQueryHandler(QueryHandler): #Fahmy
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)

    def getById(self, category_id: str) -> pd.DataFrame:
        conn = sqlite3.connect(self.dbPathOrUrl)

        query = """
        SELECT *
        FROM categories
        WHERE category_id = ?
        """

        df = pd.read_sql_query(query, conn, params=(category_id,))
        conn.close()
        return df
