class IdentifiableEntity(object): # CLAUDIA 
    def __init__(self, identifier):
        if type(identifier) == list:
            self.id = []
            for id in identifier:
                self.id.append(id)
             
    def getIds(self):
        listIds = list()
        if type(self.id) == list:
            return self.id
        listIds.append(self.id)
        return listIds

#subclass1 of IdentifiableEntity    
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

#subclass2 of IdentifiableEntity    
class Category(IdentifiableEntity): # FAHMIDA
    def __init__(self, identifier, quartile):
        self.quartile = quartile
        super().__init__(identifier)


#method to get quartile
    def getQuartile(self):
        return self.quartile

#subclass3 of IdentifiableEntity    
class Area(IdentifiableEntity): # FAHMIDA
    pass