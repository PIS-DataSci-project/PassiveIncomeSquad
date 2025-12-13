import pandas as pd
from pandas import read_csv, DataFrame
from rdflib import Graph, URIRef, RDF, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from Entities import *

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

    
class JournalUploadHandler(UploadHandler):
    """Uploads journal data from CSV to RDF triplestore"""
    def __init__(self, dbPathOrUrl=None):
        super().__init__()
        if dbPathOrUrl:
            self.setdbPathOrUrl(dbPathOrUrl)
    
    def createGraph(self, path):
        """Create RDF graph from CSV file"""
        myGraph = Graph()
        journals = read_csv(path, keep_default_na=False,
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
            myGraph.add((subj, RDF.type, Journal))
            myGraph.add((subj, title, Literal(row["Journal title"])))
            issn = row["Journal ISSN (print version)"].strip()
            eissn = row["Journal EISSN (online version)"].strip()
            issn_and_eissn = "; ".join(filter(None, [issn, eissn]))
            if issn_and_eissn:
                myGraph.add((subj, identifier, Literal(issn_and_eissn)))
            myGraph.add((subj, language, Literal(row["Languages in which the journal accepts manuscripts"])))
            myGraph.add((subj, publisher, Literal(row["Publisher"])))
            myGraph.add((subj, seal, Literal(row["DOAJ Seal"])))
            myGraph.add((subj, license, Literal(row["Journal license"])))
            myGraph.add((subj, apc, Literal(row["APC"]))) 
        return myGraph

    def pushDataToDb(self, path):
        store = SPARQLUpdateStore()
        store.open((self.dbPathOrUrl, self.dbPathOrUrl))
        # Upload all triples to SPARQL store
        for triple in myGraph.triples((None, None, None)):
            store.add(triple)
        store.close()


