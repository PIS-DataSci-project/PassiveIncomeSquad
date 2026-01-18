#SUGGEST: Peroni said to be explicit so we should add the superclass (object) to the classes when it is not explicit --> eg. IndentifiableEntity(object) and so the others too if it is not too much

#superclass
class IdentifiableEntity: # CLAUDIA 
    def __init__(self, identifier): #def __init__ is needed to define the constructor and self is the very first parameter that does a self reference to the object i am trying to create when i run the constructor
        if type(identifier) == list: #when there are 1...* idenifiers he puts in plural and then below and then add for set but here since you decided list you used append right? also is ==list = a =list()?
            self.id = []
            for id in identifier:
                self.id.append(id)
            self.identifier = self.id
        self.identifier = identifier 

  #method to get the ids
    def getIds(self):
        if type(self.identifier) == list:
            return self.identifier
        ListIds = list()
        ListIds.append(self.identifier)
        return ListIds

#subclass1 of IdentifiableEntity    
class Journal(IdentifiableEntity): # CLAUDIA 
    def __init__(self, identifier, title, language, publisher, seal, license, apc, hasCategory, hasArea): #hasCategory and hasArea for the relation through arrows
        super().__init__(identifier) # clooo we need to put this after self.hasArea = hasArea
        self.title = title
        self.publisher = publisher
        self.language = language
        self.seal = seal
        self.license = license #why is it yellow? hahaha
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

#subclass2 of IdentifiableEntity    
class Category(IdentifiableEntity): # FAHMIDA
    def __init__(self, identifier, quartile): #identifier added because inherited from superclass
        self.quartile = quartile #handle new thing first then add the things handled by superclass he said
        super().__init__(identifier) #here is where the constructor is recalled explicitly to handle the input parameter identifier


    #method to get quartile
    def getQuartile(self):
        return self.quartile

#subclass3 of IdentifiableEntity    
class Area(IdentifiableEntity): # FAHMIDA
    pass #nothing happened here + the constructor has been also inherited from superclass so i dont need to write it again

#CLASSESS ARE OFFICIALY DONE!!!! IMPLEMENTATION OF DATA MODEL DONEE