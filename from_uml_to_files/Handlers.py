#ALL IMPORTS AT THE TOP OF THE FILE
#General imports
from Entities import *
import pandas as pd 

#For Graph Database
from rdflib import Graph, URIRef, RDF, Literal, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import requests

#For Relational Database
import json
import sqlite3 

#---------------------------------------------------------------------------------------------
#superclass
class Handler(object): # 
    #Base handler for database connection management
    def __init__(self): # defines the constructor
        self.dbPathOrUrl = "" # initialize empty path or URL

    def getDbPathOrUrl(self):
        #Get the current database path or URL
        return self.dbPathOrUrl

    def setDbPathOrUrl(self, dbPathOrUrl):
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
class JournalUploadHandler(UploadHandler): # Claudia
    #Uploads journal data from CSV to RDF triplestore --> uploads data and tells me where it comes from
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setDbPathOrUrl(dbPathOrUrl)
    
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
        apc = URIRef("https://schema.org/processingFee") # no external interoperability, only works locally
        # Create RDF graph
        g = Graph()
        journals = pd.read_csv(path, keep_default_na=False) # Read CSV into DataFrame
        for idx, row in journals.iterrows():
            localId = "journal-" + str(idx) # unique local identifier for each journal 
            subj = URIRef(baseUrl + "/" + localId) # Subject URI for the journal
            # Add triples to the graph
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
        if not self.dbPathOrUrl:
            return False
        g = self.createGraph(path)
        store = SPARQLUpdateStore()
        endpoint = self.dbPathOrUrl
        store.open((endpoint, endpoint))
        # Upload all triples to SPARQL store
        for triple in g.triples((None, None, None)):
            store.add(triple)
        store.close()
        return True 

    def serializeToTTL(self, csv_path, output_path=None): 
        if output_path is None:
            output_path = csv_path.rsplit('.', 1)[0] + '.ttl'
        graph = self.createGraph(csv_path)
        graph.serialize(destination=output_path, format='turtle')
        return output_path
    
#CategoryUploadHandler - River HEREE 
#JSON --> DB
class CategoryUploadHandler(UploadHandler):  # River
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setDbPathOrUrl(dbPathOrUrl)

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
class JournalQueryHandler(QueryHandler):
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setDbPathOrUrl(dbPathOrUrl)

    def _escape_literal(self, value: str) -> str:

        if value is None:
            return ""
            
        return value.replace("\\", "\\\\").replace('"', '\\"')
 
    def _execute_sparql_query(self, sparql_query: str) -> pd.DataFrame:
        try:
            response = requests.get(
                self.getDbPathOrUrl(),
                params={"query": sparql_query, "format": "json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                bindings = data.get("results", {}).get("bindings", [])
                
                if not bindings:
                    return pd.DataFrame()
                
                # Transform bindings to DataFrame rows
                rows = []
                for binding in bindings:
                    row = {key: value.get("value", "") for key, value in binding.items()}
                    rows.append(row)
                
                return pd.DataFrame(rows)
            else:
                print(f"SPARQL query failed with status: {response.status_code}")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            return pd.DataFrame()
    
    def getById(self, entity_id: str) -> pd.DataFrame:
        #Get journal by ISSN or EISSN identifier
        if not entity_id:
            return pd.DataFrame()
        
        escaped_id = self._escape_literal(entity_id)
        
        sparql_query = f'''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:identifier ?identifier .
            FILTER(CONTAINS(STR(?identifier), "{escaped_id}"))
            OPTIONAL {{ ?journal schema:inLanguage ?language }}
            OPTIONAL {{ ?journal schema:publishedBy ?publisher }}
            OPTIONAL {{ ?journal schema:award ?seal }}
            OPTIONAL {{ ?journal schema:license ?license }}
            OPTIONAL {{ ?journal schema:processingFee ?apc }}
        }}
        '''
        
        return self._execute_sparql_query(sparql_query)

    def getAllJournals(self) -> pd.DataFrame:
        #Get all journals from the database
        sparql_query = '''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            OPTIONAL { ?journal schema:identifier ?identifier }
            OPTIONAL { ?journal schema:inLanguage ?language }
            OPTIONAL { ?journal schema:publishedBy ?publisher }
            OPTIONAL { ?journal schema:award ?seal }
            OPTIONAL { ?journal schema:license ?license }
            OPTIONAL { ?journal schema:processingFee ?apc }
        }
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query)
    
    def getJournalsWithTitle(self, partial_title: str) -> pd.DataFrame:
        #Get journals matching title
        if not partial_title:
            return pd.DataFrame()
        
        escaped_title = self._escape_literal(partial_title)
        
        sparql_query = f'''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            ?journal schema:title ?title .
            FILTER(CONTAINS(LCASE(?title), LCASE("{escaped_title}")))
            OPTIONAL {{ ?journal schema:identifier ?identifier }}
            OPTIONAL {{ ?journal schema:inLanguage ?language }}
            OPTIONAL {{ ?journal schema:publishedBy ?publisher }}
            OPTIONAL {{ ?journal schema:award ?seal }}
            OPTIONAL {{ ?journal schema:license ?license }}
            OPTIONAL {{ ?journal schema:processingFee ?apc }}
        }}
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query)
 
    def getJournalsPublishedBy(self, partial_publisher: str) -> pd.DataFrame:
        #Get journals matching publisher (partial match, case-insensitive)
        if not partial_publisher:
            return pd.DataFrame()
        
        escaped_publisher = self._escape_literal(partial_publisher)
        
        sparql_query = f'''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:publishedBy ?publisher .
            FILTER(CONTAINS(LCASE(?publisher), LCASE("{escaped_publisher}")))
            OPTIONAL {{ ?journal schema:identifier ?identifier }}
            OPTIONAL {{ ?journal schema:inLanguage ?language }}
            OPTIONAL {{ ?journal schema:award ?seal }}
            OPTIONAL {{ ?journal schema:license ?license }}
            OPTIONAL {{ ?journal schema:processingFee ?apc }}
        }}
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query)
    
    def getJournalsWithLicense(self, license_type: str) -> pd.DataFrame:
        #Get journals with exact license match
        if not license_type:
            return pd.DataFrame()
        
        escaped_license = self._escape_literal(license_type)
        
        sparql_query = f'''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:license ?license .
            FILTER(STR(?license) = "{escaped_license}")
            OPTIONAL {{ ?journal schema:identifier ?identifier }}
            OPTIONAL {{ ?journal schema:inLanguage ?language }}
            OPTIONAL {{ ?journal schema:publishedBy ?publisher }}
            OPTIONAL {{ ?journal schema:award ?seal }}
            OPTIONAL {{ ?journal schema:processingFee ?apc }}
        }}
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query)
 
    def getJournalsWithAPC(self) -> pd.DataFrame:
        #Get journals that have an Article Processing Charge
        sparql_query = '''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            ?journal schema:processingFee ?apc .
            FILTER(?apc = true)
            OPTIONAL { ?journal schema:identifier ?identifier }
            OPTIONAL { ?journal schema:inLanguage ?language }
            OPTIONAL { ?journal schema:publishedBy ?publisher }
            OPTIONAL { ?journal schema:award ?seal }
            OPTIONAL { ?journal schema:license ?license }
        }
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query) 
 
    def getJournalsWithDOAJSeal(self) -> pd.DataFrame:
        #Get journals that have a DOAJ Seal
        sparql_query = '''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            ?journal schema:award ?seal .
            FILTER(?seal = true)
            OPTIONAL { ?journal schema:identifier ?identifier }
            OPTIONAL { ?journal schema:inLanguage ?language }
            OPTIONAL { ?journal schema:publishedBy ?publisher }
            OPTIONAL { ?journal schema:license ?license }
            OPTIONAL { ?journal schema:processingFee ?apc }
        }
        ORDER BY ?title
        '''
        
        return self._execute_sparql_query(sparql_query)

# CategoryQueryHandler
# Subclass of QueryHandler
class CategoryQueryHandler(QueryHandler):
    """
    Handles queries on the relational database 'categories' table.
    Returns pandas DataFrames with:
    - category_id
    - quartile
    - identifiers
    - areas
    """

    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setDbPathOrUrl(dbPathOrUrl)

    # -----------------------------
    # Get by category_id
    # -----------------------------
    def getById(self, category_id) -> pd.DataFrame:
        query = """
        SELECT category_id, quartile, identifiers, areas
        FROM categories
        WHERE category_id = ?
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=(category_id,))
        conn.close()
        return df

    # -----------------------------
    # Get all categories
    # -----------------------------
    def getAllCategories(self) -> pd.DataFrame:
        query = """
        SELECT DISTINCT category_id, quartile, identifiers, areas
        FROM categories
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # -----------------------------
    # Get all distinct areas
    # -----------------------------
    def getAllAreas(self) -> pd.DataFrame:
        query = """
        SELECT DISTINCT areas
        FROM categories
        WHERE areas IS NOT NULL
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Split comma-separated values into individual rows
        df["area"] = df["areas"].str.split(",")
        df = df.explode("area")
        df = df[["area"]].dropna().drop_duplicates().reset_index(drop=True)
        return df

    # -----------------------------
    # Get categories filtered by quartile(s)
    # -----------------------------
    def getCategoriesWithQuartile(self, quartiles) -> pd.DataFrame:
        if not quartiles:
            return pd.DataFrame()
        placeholders = ",".join(["?"] * len(quartiles))
        query = f"""
        SELECT category_id, quartile, identifiers, areas
        FROM categories
        WHERE quartile IN ({placeholders})
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=tuple(quartiles))
        conn.close()
        return df

    # -----------------------------
    # Get categories assigned to specific areas
    # -----------------------------
    def getCategoriesAssignedToAreas(self, area_ids) -> pd.DataFrame:
        if not area_ids:
            return pd.DataFrame()
        conditions = " OR ".join(["areas LIKE ?"] * len(area_ids))
        params = [f"%{area}%" for area in area_ids]
        query = f"""
        SELECT DISTINCT category_id, quartile, identifiers, areas
        FROM categories
        WHERE {conditions}
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    # -----------------------------
    # Get areas assigned to specific categories
    # -----------------------------
    def getAreasAssignedToCategories(self, category_ids) -> pd.DataFrame:
        if not category_ids:
            return pd.DataFrame()
        placeholders = ",".join(["?"] * len(category_ids))
        query = f"""
        SELECT DISTINCT areas
        FROM categories
        WHERE category_id IN ({placeholders})
          AND areas IS NOT NULL
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=tuple(category_ids))
        conn.close()

        df["area"] = df["areas"].str.split(",")
        df = df.explode("area")
        df = df[["area"]].dropna().drop_duplicates().reset_index(drop=True)
        return df
