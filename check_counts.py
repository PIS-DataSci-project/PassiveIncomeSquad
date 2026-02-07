from impl import CategoryQueryHandler

# Use the relational DB in repo root
db = './relational.db'
qh = CategoryQueryHandler(dbPathOrUrl=db)

print('getAllCategories:', len(qh.getAllCategories()))
print('getAllAreas:', len(qh.getAllAreas()))
print("getCategoriesWithQuartile({'Q1','Q2'}):", len(qh.getCategoriesWithQuartile({'Q1','Q2'})))
print("getCategoriesAssignedToAreas({'Biochemistry, Genetics and Molecular Biology'}):", len(qh.getCategoriesAssignedToAreas({'Biochemistry, Genetics and Molecular Biology'})))
print("getAreasAssignedToCategories({'Cell Biology'}):", len(qh.getAreasAssignedToCategories({'Cell Biology'})))
