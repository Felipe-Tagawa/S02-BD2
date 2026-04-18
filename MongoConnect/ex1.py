from pymongo import MongoClient
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
client = MongoClient("mongodb://localhost:27017/")

db = client['dbworld']
paises = db.countries

results = paises.find({'region':'Americas', 'area':{'$lt':100}})

for pais in results:
    print(pais)
