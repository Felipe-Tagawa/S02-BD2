from neo4j import GraphDatabase
from pymongo import MongoClient
import pytest

# --- CLASSE NEO4J ---
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# --- CLASSE MONGODB ---
class MongoConnection:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        return self.collection.insert_one(data)

    def find_data(self, query):
        return list(self.collection.find(query))

    def update_data(self, query, new_values):
        return self.collection.update_one(query, {"$set": new_values})

    def delete_data(self, query):
        return self.collection.delete_one(query)

# --- CONFIGURAÇÕES ---
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "projeto_s02"
COLLECTION = "pessoas"

# --- EXECUÇÃO DOS TESTES ---

print("🚀 Iniciando testes de conexão...")

try:
    # 1. Testando Neo4j
    conn_neo4j = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    query_create = """
    MERGE (f:Person {name: 'Felipe'}) 
    SET f.age = 21, f.role = 'Backend Developer'
    RETURN f
    """
    conn_neo4j.execute_query(query_create)
    print("✅ Neo4j: Nó 'Felipe' criado/atualizado.")

    # 2. Testando MongoDB
    conn_mongo = MongoConnection(MONGO_URI, DB_NAME, COLLECTION)
    
    # Criar (Insert)
    felipe_doc = {
        "name": "Felipe",
        "age": 21,
        "role": "Backend Developer",
        "hobbies": ["Docker", "Python", "Café"]
    }
    res = conn_mongo.insert_data(felipe_doc)
    print(f"✅ MongoDB: Documento inserido com ID: {res.inserted_id}")

    # Buscar (Read)
    busca = conn_mongo.find_data({"name": "Felipe"})
    print(f"🔍 MongoDB: Encontrado: {busca[0]['name']} - {busca[0]['role']}")

    # Atualizar (Update)
    conn_mongo.update_data({"name": "Felipe"}, {"status": "Online e Operante"})
    print("✅ MongoDB: Documento atualizado.")

    # Fechar conexões
    conn_neo4j.close()
    print("\n🏁 Todos os testes concluídos com sucesso!")

except Exception as e:
    print(f"\n❌ Erro durante os testes: {e}")
    print("Verifique se os containers Docker estão rodando (s02pv1).")