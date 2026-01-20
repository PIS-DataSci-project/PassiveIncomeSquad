#----------------------------------------------------------------------
# ENTITIES 
#----------------------------------------------------------------------

class IdentifiableEntity(object): # CLAUDIA 
    def __init__(self, identifiers): 
        self.id = list()
        for id in identifiers:
            self.id.append(id)
             
    def getIds(self):
        listIds = list()
        for id in self.id:
            listIds.append(id)
        listIds.sort() # sort the list of IDs
        return listIds

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
        listLangs = list()
        for lang in self.language:
            listLangs.append(lang)
        listLangs.sort() # sort the list of languages
        return listLangs

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

