#ALL IMPORTS AT THE TOP OF THE FILE
#General imports
import pandas as pd 

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
        
        # Clean and convert data types
        journals["Publisher"] = journals["Publisher"].fillna("").astype(str).str.strip()
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:identifier ?identifiers .
            FILTER(CONTAINS(STR(?identifiers), "{escaped_id}"))
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            OPTIONAL { ?journal schema:identifier ?identifiers }
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            ?journal schema:title ?title .
            FILTER(CONTAINS(LCASE(?title), LCASE("{escaped_title}")))
            OPTIONAL {{ ?journal schema:identifier ?identifiers }}
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:publishedBy ?publisher .
            FILTER(CONTAINS(LCASE(?publisher), LCASE("{escaped_publisher}")))
            OPTIONAL {{ ?journal schema:identifier ?identifiers }}
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {{
            ?journal rdf:type schema:Periodical .
            OPTIONAL {{ ?journal schema:title ?title }}
            ?journal schema:license ?license .
            FILTER({license_filter})
            OPTIONAL {{ ?journal schema:identifier ?identifiers }}
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            ?journal schema:processingFee ?apc .
            FILTER(?apc = true)
            OPTIONAL { ?journal schema:identifier ?identifiers }
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
        
        SELECT ?journal ?title ?identifiers ?language ?publisher ?seal ?license ?apc
        WHERE {
            ?journal rdf:type schema:Periodical .
            OPTIONAL { ?journal schema:title ?title }
            ?journal schema:award ?seal .
            FILTER(?seal = true)
            OPTIONAL { ?journal schema:identifier ?identifiers }
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
        Returns: Journal or Category, or None
        """
        if not entity_id:
            return None
            
        # 1. Search in journal handlers (Blazegraph)
        journal_dfs = []
        for handler in self.journalQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                journal_dfs.append(result_df)
        
        # Merge and remove duplicates from journal results
        if journal_dfs:
            merged = pd.concat(journal_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Parse identifiers from the identifier field (may contain multiple IDs separated by "; ")
                identifiers = []
                if 'identifier' in row and pd.notna(row['identifier']):
                    id_str = str(row['identifier'])
                    identifiers = [id.strip() for id in id_str.split(';') if id.strip()]
                
                if not identifiers: 
                    identifiers = [entity_id]
                
                # Parse languages from the language field (may contain multiple languages)
                languages = []
                if 'language' in row and pd.notna(row['language']):
                    lang_str = str(row['language'])
                    languages = [lang.strip() for lang in lang_str.split(',') if lang.strip()]
                
                # Get categories and areas using helper methods
                categories = self.getCategoriesByJournalId(identifiers)
                areas = self.getAreasByJournalId(identifiers)
                
                # Convert boolean strings to actual booleans
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
        
        # 2. Search in category handlers (SQLite)
        category_dfs = []
        for handler in self.categoryQuery:
            result_df = handler.getById(entity_id)
            if result_df is not None and not result_df.empty:
                category_dfs.append(result_df)
        
        # Merge and remove duplicates from category results
        if category_dfs:
            merged = pd.concat(category_dfs, ignore_index=True).drop_duplicates()
            if not merged.empty:
                row = merged.iloc[0]
                
                # Return Category
                identifiers = []
                if 'identifiers' in row and pd.notna(row['identifiers']):
                    identifiers.append(str(row['identifiers']))
                
                return Category(
                    identifiers=list(set(identifiers)) if identifiers else [entity_id],
                    quartile=str(row.get('quartile', ''))
                )
        
        # 3. If not found as journal in Blazegraph or as category, check if we have category/area data for this identifier
        categories = self.getCategoriesByJournalId(entity_id)
        areas = self.getAreasByJournalId(entity_id)
        
        if categories or areas:
            # Found category/area data, return minimal Journal object
            return Journal(
                identifiers=[entity_id],
                title="",
                language=[],
                seal=False,
                license="",
                apc=False,
                publisher="",
                categories=categories,
                areas=areas
            )
        
        # 4. Not found in any database
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