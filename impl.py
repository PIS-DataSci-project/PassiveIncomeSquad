#ALL IMPORTS AT THE TOP OF THE FILE
#General imports
import pandas as pd 
from typing import List, Set, Dict

#For Graph Database
from rdflib import Graph, URIRef, RDF, Literal, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import requests

#For Relational Database
import json
import sqlite3 


#----------------------------------------------------------------------
# ENTITIES 
#----------------------------------------------------------------------

class IdentifiableEntity(object): # CLAUDIA 
    def __init__(self, identifiers): 
        self.identifiers = list()
        for identifier in identifiers:
            self.identifiers.append(identifier)
             
    def getIds(self):
        list_ids = list()
        for identifier in self.identifiers:
            list_ids.append(identifier)
        list_ids.sort() # sort the list of IDs
        return list_ids
    
#subclass1 of IdentifiableEntity    
class Journal(IdentifiableEntity): # CLAUDIA 
    def __init__(self, identifiers, title, language, seal, license, apc, publisher=None, categories=None, areas=None):
        self.title = title
        self.publisher = publisher if publisher else ""
        self.language = language
        self.seal = True if seal else False
        self.license = license
        self.apc = True if apc else False
        self.categories = categories if categories is not None else []
        self.areas = areas if areas is not None else []
        super().__init__(identifiers)
        
    def getTitle(self):
        return self.title

    def getPublisher(self): 
        return self.publisher
    
    def hasPublisher(self, publisher): 
        if self.publisher == publisher:
            return True
        return False
    
    def getLanguage(self):
        list_langs = list()
        for lang in self.language:
            list_langs.append(lang)
        list_langs.sort() # sort the list of languages
        return list_langs
    
    def hasDOAJSeal(self): # boolean
        return self.seal
    
    def getLicense(self):
        return self.license
    
    def hasAPC(self): # boolean
        return self.apc

    def getCategories(self):
        return self.categories 
    
    def hasCategory(self, category):
        return category in self.categories
    
    def getAreas(self): 
        return self.areas    
        
    def hasArea(self, area): 
        return area in self.areas

#subclass2 of IdentifiableEntity    
class Category(IdentifiableEntity): # FAHMIDA
    def __init__(self, identifiers, quartile):
        self.quartile = quartile
        super().__init__(identifiers)


#method to get quartile
    def getQuartile(self):
        return self.quartile

#subclass3 of IdentifiableEntity    
class Area(IdentifiableEntity): # FAHMIDA
    pass

#----------------------------------------------------------------------
# HANDLERS 
#----------------------------------------------------------------------
#superclass
class Handler(object): # CLAUDIA
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
class UploadHandler(Handler): #RIVER 
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
            self.setDbPathOrUrl(dbPathOrUrl)
    
    def createGraph(self, path):
        #Create RDF graph from CSV file
        # URI Definitions
        base_url = "https://github.com/PassiveIncomeSquad/PIS-DataSci-project"
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
        journals = pd.read_csv(path, keep_default_na=False)
        # Strip whitespace from column names
        journals.columns = journals.columns.str.strip()

        # Clean and convert data types
        journals["Publisher"] = journals["Publisher"].fillna("").astype(str).str.strip()
        
        # Clean and convert data types
        journals["Journal ISSN (print version)"] = journals["Journal ISSN (print version)"].astype(str).str.strip()
        journals["Journal EISSN (online version)"] = journals["Journal EISSN (online version)"].astype(str).str.strip()
        journals['DOAJ Seal'] = journals['DOAJ Seal'].str.lower() == 'yes'
        journals['APC'] = journals['APC'].str.lower() == 'yes'
        
        for idx, row in journals.iterrows(): 
            local_id = "journal-" + str(idx) 
            subj = URIRef(base_url + "/" + local_id)
            g.add((subj, RDF.type, Journal))
            g.add((subj, title, Literal(row["Journal title"])))
            
            # Combine ISSN and EISSN
            issn = row["Journal ISSN (print version)"]
            eissn = row["Journal EISSN (online version)"]
            issn_and_eissn = "; ".join(filter(None, [issn, eissn]))
            if issn_and_eissn:
                g.add((subj, identifier, Literal(issn_and_eissn)))    
            
            g.add((subj, language, Literal(row["Languages in which the journal accepts manuscripts"])))
            g.add((subj, publisher, Literal(row["Publisher"])))
            g.add((subj, license, Literal(row["Journal license"])))
            g.add((subj, seal, Literal(row["DOAJ Seal"], datatype=XSD.boolean)))
            g.add((subj, apc, Literal(row["APC"], datatype=XSD.boolean)))
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
    
    def getJournalsWithLicense(self, licenses: str) -> pd.DataFrame:
        #Get journals with exact license match
        if not licenses:
            return self.getAllJournals()
        
        # Build the license filter
        escaped_licenses = [
            f'"{self._escape_literal(license)}"' for license in licenses if license
        ]

        if not escaped_licenses:
            return pd.DataFrame()
        
        license_filter = " || ".join(
            [f"?license = {license}" for license in escaped_licenses]
        )
        
        sparql_query = f'''
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?journal ?title ?identifier ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:license ?license .
            FILTER({license_filter})
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
class CategoryQueryHandler(QueryHandler): #FAHMIDA
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
    
    # -----------------------------
    # Get categories by journal identifier
    # -----------------------------
    def getCategoriesByJournalId(self, journal_id) -> pd.DataFrame:
        """
        Returns categories associated with a specific journal identifier.
        """
        query = """
        SELECT category_id, quartile, identifiers, areas
        FROM categories
        WHERE identifiers = ?
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=(journal_id,))
        conn.close()
        return df

    # -----------------------------
    # Get areas by journal identifier
    # -----------------------------
    def getAreasByJournalId(self, journal_id) -> pd.DataFrame:
        """
        Returns areas associated with a specific journal identifier.
        """
        query = """
        SELECT DISTINCT areas
        FROM categories
        WHERE identifiers = ?
          AND areas IS NOT NULL
        """
        conn = sqlite3.connect(self.getDbPathOrUrl())
        df = pd.read_sql_query(query, conn, params=(journal_id,))
        conn.close()
        
        # Split comma-separated values into individual rows
        if not df.empty:
            df["area"] = df["areas"].str.split(",")
            df = df.explode("area")
            df = df[["area"]].dropna().drop_duplicates().reset_index(drop=True)
        
        return df


# -----------------------------------------------------------------------------------
# QUERY ENGINE 
# -----------------------------------------------------------------------------------

#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine: #Fahmida
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
    #  METHODS
    # ---------------------------------------------------------

    def cleanJournalHandlers(self) -> bool: #Claudia
        """Clear all Journal Query Handlers"""
        self.journalQuery.clear() # remove all elements from the list
        return True # indicate success
    
    def cleanCategoryHandlers(self) -> bool: #Claudia
        """Clear all Category Query Handlers"""
        self.categoryQuery.clear()
        return True
    
    def addJournalHandler(self, handler: JournalQueryHandler) -> bool:  # River
        self.journalQuery.append(handler)
        return True

    def addCategoryHandler(self, handler: CategoryQueryHandler) -> bool:  # River
        self.categoryQuery.append(handler)
        return True
    
    def getCategoriesByJournalId(self, journal_id) -> list: # Claudia # additional
        """
        Get all Category objects for journal identifiers.
        Transforms DataFrames from CategoryQueryHandler into Category objects.
        """
        if isinstance(journal_id, str):
            journal_ids = [journal_id]
        else:
            journal_ids = journal_id
        
        categories = []
        for handler in self.categoryQuery:
            for journal_id in journal_ids:
                cat_df = handler.getCategoriesByJournalId(journal_id)
                if cat_df is not None and not cat_df.empty:
                    for _, row in cat_df.iterrows():
                        cat = Category(
                            identifiers=[str(row['category_id'])],
                            quartile=str(row.get('quartile', ''))
                        )
                        categories.append(cat)
        
        # Remove duplicates based on category_id
        unique_categories = []
        seen_ids = set()
        for cat in categories:
            cat_id = cat.getIds()[0] if cat.getIds() else None
            if cat_id and cat_id not in seen_ids:
                seen_ids.add(cat_id)
                unique_categories.append(cat)
        
        return unique_categories

    # ---------------------------------------------------------

    def getAreasByJournalId(self, journal_id) -> list: # Claudia # additional
        """
        Get all Area objects for journal identifiers.
        Transforms DataFrames from CategoryQueryHandler into Area objects.
        """
        if isinstance(journal_id, str):
            journal_ids = [journal_id]
        else:
            journal_ids = journal_id
        
        areas = []
        for handler in self.categoryQuery:
            for journal_id in journal_ids:
                area_df = handler.getAreasByJournalId(journal_id)
                if area_df is not None and not area_df.empty:
                    for _, row in area_df.iterrows():
                        if 'area' in row and pd.notna(row['area']):
                            area_name = str(row['area']).strip()
                            if area_name:
                                area = Area(identifiers=[area_name])
                                areas.append(area)
        
        # Remove duplicates based on area identifier
        unique_areas = {}
        for area in areas:
            area_id = area.getIds()[0] if area.getIds() else None
            if area_id and area_id not in unique_areas:
                unique_areas[area_id] = area
        
        return list(unique_areas.values())
    
    # --------------------------------------------------
    
    def getEntityById(self, entity_id: str):
        """
        Search for entity by ID in all databases.
        Returns: IdentifiableEntity (Journal, Category, or Area), or None
        """
        if not entity_id:
            return None
            
        # 1. Try to find as a Journal (by ISSN/EISSN)
        journal_dfs = []
        for handler in self.journalQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                journal_dfs.append(result_df)
        
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Parse identifiers
                identifiers = []
                if 'identifier' in row and pd.notna(row['identifier']):
                    id_str = str(row['identifier'])
                    identifiers = [id.strip() for id in id_str.split(';') if id.strip()]
                
                if not identifiers: 
                    identifiers = [entity_id]
                
                # Parse languages
                languages = []
                if 'language' in row and pd.notna(row['language']):
                    lang_str = str(row['language'])
                    languages = [lang.strip() for lang in lang_str.split(',') if lang.strip()]
                
                # Get categories and areas
                categories = self.getCategoriesByJournalId(identifiers)
                areas = self.getAreasByJournalId(identifiers)
                
                # Convert booleans
                seal = False
                if 'seal' in row:
                    if isinstance(row['seal'], str):
                        seal = row['seal'].lower() == 'true'
                    else:
                        seal = bool(row['seal'])
                
                apc = False
                if 'apc' in row:
                    if isinstance(row['apc'], str):
                        apc = row['apc'].lower() == 'true'
                    else:
                        apc = bool(row['apc'])
                
                return Journal(
                    identifiers=identifiers,
                    title=str(row.get('title', '')),
                    language=languages,
                    seal=seal,
                    license=str(row.get('license', '')),
                    apc=apc,
                    publisher=str(row.get('publisher', '')),
                    categories=categories,
                    areas=areas
                )
        
        # 2. Try to find as a Category (by category_id)
        for handler in self.categoryQuery:
            all_cats = handler.getAllCategories()
            if not all_cats.empty:
                matching = all_cats[all_cats['category_id'] == entity_id]
                if not matching.empty:
                    row = matching.iloc[0]
                    return Category(
                        identifiers=[str(row['category_id'])],
                        quartile=str(row.get('quartile', ''))
                    )
        
        # 3. Try to find as an Area (by area name/id)
        for handler in self.categoryQuery:
            all_areas = handler.getAllAreas()
            if not all_areas.empty:
                matching = all_areas[all_areas['area'] == entity_id]
                if not matching.empty:
                    return Area(identifiers=[entity_id])
        
        # 4. Not found
        return None
       
       
    # ============================================
    # JOURNAL-RELATED METHODS (Polina)
    # ============================================
    def getAllJournals(self) -> list:
        #Get all the journals
        all_dfs = [handler.getAllJournals() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsWithTitle(self, partialTitle: str) -> list:
        # find all the journals with a partial title match
        all_dfs = [handler.getJournalsWithTitle(partialTitle) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsPublishedBy(self, partialName: str) -> list:
        #get the journals published by a publisher
        all_dfs = [handler.getJournalsPublishedBy(partialName) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]
 
    # ---------------------------------------------------------

    def getJournalsWithLicense(self, licenses: set) -> list:
        # get all the journals with a license
        all_dfs = [handler.getJournalsWithLicense(licenses) for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()

        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------

    def getJournalsWithAPC(self) -> list:
        #get all the journals with APC
        all_dfs = [handler.getJournalsWithAPC() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
        
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]

    # ---------------------------------------------------------
    
    def getJournalsWithDOAJSeal(self) -> list:
        # get all the journals with DOAJ Seal
        all_dfs = [handler.getJournalsWithDOAJSeal() for handler in self.journalQuery]
        merged = pd.concat(all_dfs).drop_duplicates() if all_dfs else pd.DataFrame()
    
        return [
            Journal(
                identifiers=[i.strip() for i in str(row['identifier']).split(';') if i.strip()],
                title=row.get('title', ''),
                language=[l.strip() for l in str(row.get('language', '')).split(',') if l.strip()],
                seal=str(row.get('seal', 'false')).lower() == 'true',
                license=row.get('license', ''),
                apc=str(row.get('apc', 'false')).lower() == 'true',
                publisher=row.get('publisher', '')
            )
            for _, row in merged.iterrows()
        ]
        
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
    
#------------------------------------------------
#FullQueryEngine
#------------------------------------------------
class FullQueryEngine(BasicQueryEngine):
    """
    FullQueryEngine = “跨源拼接查询”的 QueryEngine。

    它做的事不是“替代” BasicQueryEngine，而是在 BasicQueryEngine 的基础上做 mashup：
    1) 先用 CategoryQueryHandler（SQLite）查出一批 journal identifiers（ISSN/EISSN）。
    2) 再用 JournalQueryHandler（图数据库 / SPARQL）把这些 identifiers 对应的 journals 查出来。
    3) 最后返回 Journal 对象列表（领域对象），而不是 DataFrame。

    设计风格对齐 BasicQueryEngine：
    - handler 负责查 df
    - engine 负责把 df 变成对象（复用类似 _add_journals_from_df 的“翻译器”思路）
    """

    def __init__(self, journalQuery=None, categoryQuery=None):
        # 原 River_full.py 的 super().__init__(journalQuery or [], categoryQuery or [])
        # 但你现有 BasicQueryEngine.__init__ 不接参数，所以这里做“等价初始化”：
        super().__init__()
        if journalQuery:
            self.journalQuery.extend(journalQuery)
        if categoryQuery:
            self.categoryQuery.extend(categoryQuery)

    # --------------------------
    # 1) Parse：你要求“必须用”
    # --------------------------
    def _parse_list_field(self, raw) -> List[str]:
        """
        把数据库/df 里可能出现的“粘连字符串字段”拆成 list。

        为什么需要：
        - identifiers 可能是 "1234-5678; 8765-4321" 或 "1234-5678,8765-4321"
        - language 可能是 "English; Italian"
        - 有时也可能是 None / 空串

        我们不处理 bool（按你的要求），这里只做“字符串拆分”。
        """
        if raw is None:
            return []
        text = str(raw).strip()
        if not text:
            return []

        # 兼容两种常见分隔符：; 和 ,
        text = text.replace(";", ",")
        parts = [p.strip() for p in text.split(",")]
        return [p for p in parts if p]

    # --------------------------------------------
    # 2) 辅助：从 categories df “翻译”出 identifiers 集合
    # --------------------------------------------
    def _add_identifiers_from_categories_df(self, df: pd.DataFrame, identifiers: Set[str]) -> None:
        if df is None or df.empty:
            return

        # 兼容列名：有的地方叫 identifiers，有的地方可能叫 identifier
        col = "identifiers" if "identifiers" in df.columns else "identifier"
        if col not in df.columns:
            return

        for _, row in df.iterrows():
            for one_id in self._parse_list_field(row.get(col)):
                identifiers.add(one_id)

    # ---------------------------------------------------
    # 3) 辅助：从 journals df 中挑出“匹配 identifiers 的行”
    # ---------------------------------------------------
    def _add_journals_matching_identifiers_from_df(
        self,
        df: pd.DataFrame,
        wanted_identifiers: Set[str],
        journal_map: Dict[str, Journal],
    ) -> None:
        if df is None or df.empty or not wanted_identifiers:
            return

        id_col = "identifier" if "identifier" in df.columns else "identifiers"
        if id_col not in df.columns:
            return

        for _, row in df.iterrows():
            row_ids = self._parse_list_field(row.get(id_col))
            if not row_ids:
                continue

            hit = any(one_id in wanted_identifiers for one_id in row_ids)
            if not hit:
                continue

            key = row_ids[0]

            if key not in journal_map:
                journal_map[key] = Journal(
                    identifiers=row_ids,
                    title=row.get("title", ""),
                    language=self._parse_list_field(row.get("language")),
                    seal=row.get("seal", False),      # bool 暂且不处理，直接传
                    license=row.get("license", ""),
                    apc=row.get("apc", False),        # bool 暂且不处理，直接传
                    publisher=row.get("publisher", None),
                )

    # ==========================
    # Mashup 查询 1
    # ==========================
    def getJournalsInCategoriesWithQuartile(
        self,
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}

        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 2
    # ==========================
    def getJournalsInAreasWithLicense(
        self,
        area_ids: Set[str],
        licenses: Set[str],
    ) -> List[Journal]:
        if not area_ids or not licenses:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 3
    # ==========================
    def getDiamondJournalsInAreasAndCategoriesWithQuartile(
        self,
        area_ids: Set[str],
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not area_ids or not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]
            if "quartile" in df.columns:
                df = df[df["quartile"].isin(quartiles)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())