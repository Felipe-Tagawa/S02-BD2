from cassandra.cluster import Cluster
from uuid import uuid4

cluster = Cluster(['localhost'])

try:
    session = cluster.connect()

    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS my_keyspace
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """
    )

    session.set_keyspace('my_keyspace')

    # Criar tabelas 
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id UUID PRIMARY KEY,
            nome TEXT,
            idade INT
        )
        """
    )

    # Inserir Dados
    session.execute(
        """
        INSERT INTO usuarios (id, nome, idade)
        VALUES (%s, %s, %s)
        """, 
        (uuid4(), 'João', 25)
    )

    # Consultar
    rows = session.execute("SELECT * FROM usuarios")
    for row in rows:
        print(row.id, row.nome, row.idade)

except Exception as e:
    print(f"Ocorreu um erro: {e}")

finally:
    cluster.shutdown()