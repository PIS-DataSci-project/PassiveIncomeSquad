# CLASSES

class IdentifiableEntity:
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
        ListIDS = list()
        ListIDS.append(self.identifier)
        return ListIDS

class Category(IdentifiableEntity):
    def __init__(self, identifier, quartile):
        super().__init__(identifier)
        self.quartile = quartile
        self.identifier = identifier
    
    def getQuartile(self):
        return self.quartile

class Area(IdentifiableEntity):
    def __init__(self, identifier):
        super().__init__(identifier)
        self.identifier = identifier

class Journal(IdentifiableEntity):
    def __init__(self, identifier, title, language, publisher, seal, license, apc):
        super().__init__(identifier)
        self.title = title
        self.publisher = publisher
        self.language = language
        self.seal = seal
        self.license = license
        self.apc = apc
        
    def getTitle(self):
        return self.title

    def getPublisher(self):
        return self.publisher
    
    def getLanguage(self):
        return self.language

    def getDOAJSeal(self):
        return self.seal
    
    def getLicense(self):
        return self.license

    def getAPC(self):
        return self.apc
    
    # def getCategories(self):
        # boh if type(self.categories) == list:
        #     return self.categories
        # listIDS = list()
        # listIDS.append(self.categories)
        # return listIDS
    
    # def getAreas(self):
        # boh
