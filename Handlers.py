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
#JSON --> DB
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
class JournalQueryHandler(QueryHandler):
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)

    def _escape_literal(self, value: str) -> str:

        if value is None:
            return ""
            
        return value.replace("\\", "\\\\").replace('"', '\\"')
 
    def _execute_sparql_query(self, sparql_query: str) -> pd.DataFrame:
        try:
            response = requests.get(
                self.getdbPathOrUrl(),
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
class CategoryQueryHandler(QueryHandler): #Fahmida
    """
    DOCSTRING: This is a documentation string for the class itself.
    It explains what the class does, how it queries the relational database,
    and what kind of output (pandas DataFrame) it returns.
    """

    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)

    # --------------------------------------------------
    # OVERRIDDEN METHOD: getById
    # --------------------------------------------------
    def getById(self, category_id: str) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves all rows related to a given category ID.
        This overrides the abstract method defined in QueryHandler.
        """
        # SQL STRING LITERAL: This string contains the SQL query to execute
        query = """
        SELECT category_id, quartile, identifiers, areas
        FROM categories
        WHERE category_id = ?
        """
        return pd.read_sql_query(
            query,
            self.getdbPathOrUrl(),
            params=(category_id,)
        )

    # --------------------------------------------------
    # Return all category records
    # --------------------------------------------------
    def getAllCategories(self) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves all categories from the relational database.
        Columns returned:
        - category_id
        - quartile
        - identifiers (journal identifier)
        - areas (comma-separated string)
        """
        query = """
        SELECT DISTINCT category_id, quartile, identifiers, areas
        FROM categories
        """  # SQL STRING LITERAL
        return pd.read_sql_query(query, self.getdbPathOrUrl())

    # --------------------------------------------------
    # Return all distinct areas
    # --------------------------------------------------
    def getAllAreas(self) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves all distinct areas assigned to categories.
        Since 'areas' is stored as a comma-separated string, we:
        1. Retrieve the column
        2. Split values by comma
        3. Explode them into separate rows
        """
        query = """
        SELECT DISTINCT areas
        FROM categories
        WHERE areas IS NOT NULL
        """  # SQL STRING LITERAL

        df = pd.read_sql_query(query, self.getdbPathOrUrl())

        # Split comma-separated values into lists
        df["area"] = df["areas"].str.split(",")

        # Turn lists into individual rows
        df = df.explode("area")

        # Clean and deduplicate
        df = df[["area"]].dropna().drop_duplicates().reset_index(drop=True)

        return df

    # --------------------------------------------------
    # Return categories filtered by quartile(s)
    # --------------------------------------------------
    def getCategoriesWithQuartile(self, quartiles: set[str]) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves categories belonging to one or more quartiles.
        Parameters:
        - quartiles: set of quartile strings (e.g. {"Q1", "Q2"})
        """
        if not quartiles:
            return pd.DataFrame()

        # Prepare SQL placeholders (?, ?, ?) for the IN clause
        placeholders = ",".join(["?"] * len(quartiles))

        query = f"""
        SELECT category_id, quartile, identifiers, areas
        FROM categories
        WHERE quartile IN ({placeholders})
        """  # SQL STRING LITERAL

        return pd.read_sql_query(
            query,
            self.getdbPathOrUrl(),
            params=tuple(quartiles)
        )

    # --------------------------------------------------
    # Return categories assigned to specific areas
    # --------------------------------------------------
    def getCategoriesAssignedToAreas(self, area_ids: set[str]) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves categories that are assigned to at least one
        of the specified areas.
        Uses SQL LIKE because areas are stored as comma-separated strings.
        """
        if not area_ids:
            return pd.DataFrame()

        # Build multiple LIKE conditions joined by OR
        conditions = " OR ".join(["areas LIKE ?"] * len(area_ids))
        params = [f"%{area}%" for area in area_ids]

        query = f"""
        SELECT DISTINCT category_id, quartile, identifiers, areas
        FROM categories
        WHERE {conditions}
        """  # SQL STRING LITERAL

        return pd.read_sql_query(
            query,
            self.getdbPathOrUrl(),
            params=params
        )

    # --------------------------------------------------
    # Return areas assigned to specific categories
    # --------------------------------------------------
    def getAreasAssignedToCategories(self, category_ids: set[str]) -> pd.DataFrame:
        """
        DOCSTRING: Retrieves areas associated with one or more category IDs.
        Steps:
        1. Select areas for given categories
        2. Split comma-separated values
        3. Explode into individual rows
        """
        if not category_ids:
            return pd.DataFrame()

        placeholders = ",".join(["?"] * len(category_ids))

        query = f"""
        SELECT DISTINCT areas
        FROM categories
        WHERE category_id IN ({placeholders})
          AND areas IS NOT NULL
        """  # SQL STRING LITERAL

        df = pd.read_sql_query(
            query,
            self.getdbPathOrUrl(),
            params=tuple(category_ids)
        )

        # Split and explode areas
        df["area"] = df["areas"].str.split(",")
        df = df.explode("area")

        # Clean and deduplicate
        df = df[["area"]].dropna().drop_duplicates().reset_index(drop=True)

        return df
