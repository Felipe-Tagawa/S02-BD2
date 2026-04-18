from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Credenciais atualizadas do Aura
URI = "neo4j+s://e0a8d3c6.databases.neo4j.io" # Verifique se o ID inicial está correto
USER = "e0a8d3c6"
PASSWORD = "gNge1VZqlYQZQQ165Qn1Gda2copk4s8eelbW6lSuBEM"

conn = Neo4jConnection(URI, USER, PASSWORD)

query_create = """
CREATE (f:Person {name: 'Felipe', age: 21, role: 'Backend Developer'})
CREATE (m:Person {name: 'Maria', age: 21, role: 'A Própria Eletricidade'})
CREATE (f)-[:CONHECE {since: 2023}]->(m)
RETURN f, m
"""
conn.execute_query(query_create)

query_work = """
MATCH (p:Person {name:'Felipe'})
MERGE (e:Company {name:'Inatel', city: 'Santa Rita do Sapucaí'})
MERGE (p)-[:TRABALHA_EM {horas: 22}]->(e)
RETURN p, e
"""

conn.execute_query(query_work)

query_update = """
MATCH (p:Person {name:'Maria'})
SET p.beauty = 'Infinita'
RETURN p
"""
conn.execute_query(query_update)

# Remove - Deleta Properties
# Delete - Deleta Nós e Relacionamentos.

query_remove = """
MATCH (p:Person {name:'Maria'})
REMOVE p.age
RETURN p
"""
conn.execute_query(query_remove)

query_delete = """
MATCH (p:Person {name:'Maria'})
DETACH DELETE p
RETURN p
"""
conn.execute_query(query_delete)

#conn.execute_query("MATCH (n) DETACH DELETE n")
