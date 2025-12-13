import pandas as pd
from pandas import read_csv, DataFrame
from rdflib import Graph, URIRef, RDF, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from Entities import *

# URIs of the resources 

baseUrl = "https://github.com/PassiveIncomeSquad/PIS-DataSci-project"

Journal = URIRef("https://schema.org/Periodical") 

# attributes 

title = URIRef("https://schema.org/title")
identifier = URIRef("http://schema.org/identifier") 
language = URIRef("http://schema.org/inLanguage")  # type: ignore
publisher = URIRef("http://schema.org/publishedBy") 
seal = URIRef("https://schema.org/award") # type: ignore # BOOLEAN 
license = URIRef("https://schema.org/license")
apc = URIRef("https://schema.org/processingFee") # Article Processing Charge

# relations

hasCategory = URIRef("https://schema.org/category")
hasArea = URIRef("http://schema.org/about")

class Handler: # CLAUDIA 
    def __init__(self, dbPathOrUrl=None):
        self.dbPathOrUrl = dbPathOrUrl

    def getdbPathOrUrl(self):
        return self.dbPathOrUrl

    def setdbPathOrUrl(self, dbPathOrUrl): # enables to set a new path or URL for the database to handle.
        if dbPathOrUrl.strip():
            self.dbPathOrUrl = dbPathOrUrl
            return True # ????????? 
        else:
            return False 
        
class UploadHandler(Handler): # CLAUDIA
    def __init__(self, dbPathOrUrl=None):
        super().__init__(dbPathOrUrl)

    def pushDataToDb(self, path):
        raise  # boh? 
    
class JournalUploadHandler(UploadHandler): # CLAUDIA 
    def __init__(self, dbPathOrUrl=None):
        super().__init__(dbPathOrUrl)

    def pushDataToDb(self, path): # capire cosa succede
        if path.strip(): # or .split()
            myGraph = Graph()
            store = SPARQLUpdateStore() # proxy that interacts with the triplestore
            # endpoint = [aggiungere dopo che lo creiamo]
            store.open((self.dbPathOrUrl, self.dbPathOrUrl)) # opens connection with sparql endpoint instance
            # if path.endswith(".csv"): # forse va messo qui in questaa classe specifica
            journals = read_csv(path, keep_default_na=False, # emptied the empty spaces 
                        dtype={ # specified the data type for each column 
                        "Journal title": "string",
                        "Journal ISSN (print version)": "string",  
                        "Journal EISSN (online version)": "string",
                        "Languages in which the journal accepts manuscripts": "string",
                        "Publisher": "string",
                        "DOAJ Seal": "string",
                        "Journal license": "string", 
                        "APC": "string"
                        })
            for idx, row in journals.iterrows(): # iterating every row the doc because it's a df
                localId = "journal-" + str(idx) # the url of the local entity we are going to create
                subj = URIRef(baseUrl + localId) # uriref = base url + local id: unique url
                myGraph.add((subj, RDF.type, Journal))
                myGraph.add((subj, title, Literal(row["Journal title"]))) # tuple of 3 elements: subj, pred, obj = ONE input, not three
                # Combine ISSN and EISSN into one identifier
                issn = row["Journal ISSN (print version)"].strip() if row["Journal ISSN (print version)"] else ""
                eissn = row["Journal EISSN (online version)"].strip() if row["Journal EISSN (online version)"] else ""
                combined_identifier = "; ".join(filter(None, [issn, eissn]))
                if combined_identifier:
                    myGraph.add((subj, identifier, Literal(combined_identifier)))
                myGraph.add((subj, language, Literal(row["Languages in which the journal accepts manuscripts"])))
                myGraph.add((subj, publisher, Literal(row["Publisher"])))
                myGraph.add((subj, seal, Literal(row["DOAJ Seal"])))
                myGraph.add((subj, license, Literal(row["Journal license"])))
                myGraph.add((subj, apc, Literal(row["APC"]))) 
                # myGraph.add((subj, hasCategory, internalId(row["categories"]))) #internalId 
                # myGraph.add((subj, hasArea, internalId(row["areas"])))# finisce graph (che mi sa è la mia parte)
            for triple in myGraph.triples((None, None, None)):
                store.add(triple)
            store.close()
