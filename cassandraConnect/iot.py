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
            CREATE TABLE sensor(
            id bigint, ano int, mes int, dia int, hora text, leitura float, primary key((id, ano, mes),dia,hora
            );
        """
    )

    # Inserir Dados
    session.execute(
        """
        INSERT INTO sensor (id, ano, mes, dia, hora, leitura)
        VALUES (%s, %s, %s, %s, %s, %s) 
        (25, 2021, 5, 10, '19:00', 37),
        (25, 2021, 5, 10, '18:30', 35, 'SRS', 'TexasTemp1'),
        (72, 2021, 5, 10, '19:00', 27),
        (25, 2021, 5, 11, '18:30', 36);
        """
    )

    session.execute(
        """
        UPDATE sensor SET local = 'PA' AND modelo = 'BuffaloMoist1'
        WHERE id = 25 AND ano = 2021, AND mes = 5, AND dia = 11 AND hora = '18:30';    
        """
    )

    # Consultar
    rows = session.execute("SELECT * FROM usuarios")
    for row in rows:
        print(row.id, row.nome, row.idade)

except Exception as e:
    print(f"Ocorreu um erro: {e}")

finally:
    cluster.shutdown()