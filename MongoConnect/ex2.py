from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")

db = client['dbworld']
paises = db.countries

results = paises.find({'languages.por': {'$exists':True}},
                      {'name.common':1, 'latlgn':1, '_id':0}
                      )
                                                    
for pais in results:
    print(pais)