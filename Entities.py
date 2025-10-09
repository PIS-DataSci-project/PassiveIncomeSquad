class IdentifiableEntity: # CLAUDIA 
    def __init__(self, identifier):
        if type(identifier) == list:
            self.id = []
            for id in identifier:
                self.id.append(id)
            self.identifier = self.id
        self.identifier = identifier 
  
    def getIds(self):
        if type(self.identifier) == list:
            return self.identifier
        ListIds = list()
        ListIds.append(self.identifier)
        return ListIds

class Journal(IdentifiableEntity): # CLAUDIA 
    def __init__(self, identifier, title, language, publisher, seal, license, apc, hasCategory, hasArea):
        super().__init__(identifier)
        self.title = title
        self.publisher = publisher
        self.language = language
        self.seal = seal
        self.license = license
        self.apc = apc
        self.hasCategory = hasCategory
        self.hasArea = hasArea
        
    def getTitle(self):
        return self.title

    def getPublisher(self):
        return self.publisher
    
    def getLanguage(self): # lista # vd faq sulle lingue
        return self.language

    def getDOAJSeal(self): # boolean
        return self.seal
    
    def getLicense(self):
        return self.license

    def getAPC(self): # boolean
        return self.apc
    
    def getCategories(self):
        return self.hasCategory 
    
    def getAreas(self):
        return self.hasArea    
