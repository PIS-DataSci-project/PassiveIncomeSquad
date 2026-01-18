class IdentifiableEntity(object): # CLAUDIA # 
    def __init__(self, identifiers):
        if type(identifiers) == list:
            self.id = []
            for id in identifiers:
                self.id.append(id)
            
    def getIds(self):
        listIds = list()
        if type(self.id) == list:
            return self.id
        listIds.append(self.id)
        return listIds

class Journal(IdentifiableEntity): # CLAUDIA 
    def __init__(self, identifier, title, language, publisher, seal, license, apc, hasCategory, hasArea):
        self.title = title
        self.publisher = publisher
        self.language = language
        self.seal = seal
        self.license = license
        self.apc = apc
        self.hasCategory = hasCategory
        self.hasArea = hasArea
        super().__init__(identifier)
        
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