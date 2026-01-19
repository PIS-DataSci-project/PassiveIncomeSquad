#ALL IMPORTS AT THE TOP OF THE FILE
#General imports
from Entities import *
import pandas as pd 

#For Graph Database
from rdflib import Graph, URIRef, RDF, Literal, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

#For Relational Database
import json
import sqlite3 

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
        identifier = URIRef("https://schema.org/identifier") 
        language = URIRef("https://schema.org/inLanguage")
        publisher = URIRef("https://schema.org/publishedBy") 
        seal = URIRef("https://schema.org/award")
        license = URIRef("https://schema.org/license")
        apc = URIRef("https://schema.org/processingFee")
        # Create RDF graph
        g = Graph()
        journals = pd.read_csv(path, keep_default_na=False) # Read CSV into DataFrame
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
    
    def serializeToTTL(self, csv_path, output_path=None):
        if output_path is None:
            output_path = csv_path.rsplit('.', 1)[0] + '.ttl'
        graph = self.createGraph(csv_path)
        graph.serialize(destination=output_path, format='turtle')
        print(f"✓ Saved to {output_path}")
        return output_path
    
    def pushDataToDb(self, path):
        g = self.createGraph(path)
        store = SPARQLUpdateStore()
        endpoint = self.dbPathOrUrl
        store.open((endpoint, endpoint))
        # Upload all triples to SPARQL store
        for triple in g.triples((None, None, None)):
            store.add(triple)
        store.close()

#CategoryUploadHandler - River HEREE 
#JSON --> DataFrame --> DB
class CategoryUploadHandler(UploadHandler):  # River
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

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id TEXT,
            quartile TEXT,
            identifiers TEXT,
            areas TEXT,
            PRIMARY KEY (category_id, quartile, identifiers, areas)
        )
        """)

        # ⭐ 新增：用来做 DataFrame
        rows = []

        for record in data:
            identifiers = record.get("identifiers", [])
            categories = record.get("categories", [])

            if identifiers is None:
                identifiers = []
            elif not isinstance(identifiers, list):
                identifiers = [identifiers]

            for category in categories:
                if not isinstance(category, dict):
                    continue

                category_id = category.get("id")
                quartile = category.get("quartile")
                if not (category_id and quartile):
                    continue

                areas = category.get("areas", record.get("areas"))

                if isinstance(areas, list):
                    areas_text = ",".join(map(str, areas))
                elif areas is None:
                    areas_text = None
                else:
                    areas_text = str(areas)

                for identifier in identifiers:
                    if identifier is None:
                        continue
                    identifier = str(identifier)

                    # 写数据库
                    cur.execute(
                        "INSERT OR IGNORE INTO categories (category_id, quartile, identifiers, areas) VALUES (?, ?, ?, ?)",
                        (category_id, quartile, identifier, areas_text),
                    )

                    # ⭐ 同时攒 DataFrame 的一行
                    rows.append({
                        "identifier": identifier,
                        "category_id": category_id,
                        "quartile": quartile,
                        "areas": areas_text
                    })

        conn.commit()
        conn.close()

        # ⭐ 真正生成 DataFrame
        df = pd.DataFrame(rows)
        return df


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