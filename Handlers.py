import pandas as pd
from pandas import read_csv, DataFrame
from rdflib import Graph, URIRef, RDF, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from Entities import *

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


