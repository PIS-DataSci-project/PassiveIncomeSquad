#We need to split the methods
#------------------------------------------------
#QueryEngine
#------------------------------------------------
#Superclass --> BasicQueryEngine(object)
class BasicQueryEngine: #Fahmida
    def __init__(self):
        self.journalQuery = []     # list of JournalQueryHandler --> journalQuery is an attribute that represents data, not classes! -> i'm storing objects created from that class
        self.categoryQuery = []    # list of CategoryQueryHandler --> # empty list of CategoryQueryHandler objects

#METHODSSS
cleanJournalHandlers() : boolean #Claudia
cleanCategoryHandlers() : boolean #River
addJournalHandler(handler : JournalQueryHandler) : boolean #Claudia
addCategoryHandler(handler : CategoryQueryHandler) : boolean #River
getEntityById(id : string) : IdentifiableEntity or None #Claudia
getAllJournals() : list[Journal] #Polina
getJournalsWithTitle(partialTitle : string) : list[Journal] #Polina
getJournalsPublishedBy(partialName : string) : list[Journal] #Polina
getJournalsWithLicense(licenses : set[string]) : list[Journal] #Polina
getJournalsWithAPC() : list[Journal] #Polina
getJournalsWithDOAJSeal() : list[Journal] #Polina
getAllCategories() : list[Category] #Fahmida
getAllAreas() : list[Area] #Fahmida
getCategoriesWithQuartile(quartiles : set[string]) : list[Category] #Fahmida
getCategoriesAssignedToAreas(area_ids : set[string]) : list[Category] #Fahmida
getAreasAssignedToCategories(category_ids : set[string]) : list[Area] #Fahmida

#Subclass --> FullQueryEngine(BasicQueryEngine) 