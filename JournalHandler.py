import pandas as pd
from pandas import read_csv, DataFrame
from rdflib import Graph, URIRef, RDF, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from DataModelClasses import *

# URIs of the resources 

BaseUrl = "https://github.com/PassiveIncomeSquad/PIS-DataSci-project"

Journal = URIRef("https://schema.org/Periodical") 

# attributes # BENE AGGIUNGERE IL PIU' POSSIBILE ?

title = URIRef("https://schema.org/title")
# ISSN = URIRef("http://schema.org/issn") 
# EISSN = # issn ? # custom ? # URIRef("https://schema.org/identifier")
language: URIRef("http://schema.org/Language") 
publisher: URIRef("http://schema.org/publishedBy") #publisher? 
# publisher: URIRef("http://schema.org/publisher") 
seal: URIRef("https://schema.org/award") 
license = URIRef("https://schema.org/license")
apc = URIRef("https://schema.org/---") # ?? O CUSTOM ?? 


class Handler: 
    def __init__(self, dbPathOrUrl=None):
        self.dbPathOrUrl = dbPathOrUrl

    def getdbPathOrUrl(self):
        return self.dbPathOrUrl

    def setdbPathOrUrl(self, url): # enables to set a new path or URL for the database to handle.
        if url != " ":
            self.dbPathOrUrl = url
            return True # CAPIRE 
        else:
            return False
