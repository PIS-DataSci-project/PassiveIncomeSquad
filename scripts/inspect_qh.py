from impl import CategoryQueryHandler
import os

qh = CategoryQueryHandler(dbPathOrUrl='./relational.db')
df = qh.getAllCategories()
print('df.shape =', df.shape)
print(df.head(10))
if 'category_id' in df.columns:
    print('nunique category_id =', df['category_id'].nunique())
else:
    print('columns:', df.columns.tolist())

# quartile
dfq = qh.getCategoriesWithQuartile({'Q1','Q2'})
print('\nquartile df shape =', dfq.shape)
print(dfq.head(10))
if 'category_id' in dfq.columns:
    print('nunique category_id in quartile df =', dfq['category_id'].nunique())
else:
    print('quartile columns:', dfq.columns.tolist())
