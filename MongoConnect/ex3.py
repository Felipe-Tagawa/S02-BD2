from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")

db = client['dbworld']
paises = db.countries

results = paises.find({'name.common': {'$regex': '^B'}},
                    {'name.common':1, 'area':1, '_id':0}
                      ).sort({'area':1})

for pais in results:
    print(pais)