from datetime import datetime

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

import redis

from s202_np2_revisao_models import Aluno, Curso, Matricula

class CassandraDBConnector:
        
    nodes = ['localhost']
    port = 9042   

    key_space = "plataforma_streaming"
    
    session = None

    @staticmethod
    def get_session():
        if CassandraDBConnector.session == None:
            cluster = Cluster(
                CassandraDBConnector.nodes, 
                port=CassandraDBConnector.port
            )
            CassandraDBConnector.session = cluster.connect()
            CassandraDBConnector.session.row_factory = dict_factory
            CassandraDBConnector.session.execute(""" CREATE KEYSPACE IF NOT EXISTS {} WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }} """.format(CassandraDBConnector.key_space))  # TODO comment this when using cloud provider
            CassandraDBConnector.session.set_keyspace(CassandraDBConnector.key_space)

            #CassandraDBConnector.clean_database() 

        return CassandraDBConnector.session
    
    @staticmethod
    def clean_database():
        cassandra_clean_query = f"""
            SELECT table_name FROM system_schema.tables
            WHERE keyspace_name = '{CassandraDBConnector.key_space}';
        """
        tables = CassandraDBConnector.session.execute(cassandra_clean_query)

        # Apagar todas as tabelas do Cassandra
        for table in tables:
             if "table_name" in table.keys():
                table_name = table["table_name"]
                print(f"Apagando tabela: {table_name}")
                CassandraDBConnector.session.execute(f"DROP TABLE IF EXISTS {table_name}")

    @staticmethod
    def close():
        CassandraDBConnector.session.shutdown()

class RedisDBConnector:

    redis_host = "localhost" 
    redis_port = 6379

    connection = None

    @staticmethod
    def get_connection():
        if RedisDBConnector.connection == None:
            RedisDBConnector.connection = redis.Redis(
                host=RedisDBConnector.redis_host, 
                port=RedisDBConnector.redis_port, 
                decode_responses=True
            )
            RedisDBConnector.connection.flushall()
        return RedisDBConnector.connection
    
    @staticmethod
    def close():
        RedisDBConnector.connection.close()
                                
class AlunoDAO:   

    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()
        self.redis_connection = RedisDBConnector.get_connection()
    
    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 1 a.
        query_create = ("""                         
            CREATE TABLE IF NOT EXISTS Aluno(
                id INT,
                pais TEXT,
                cidade TEXT,
                endereco TEXT,
                nome TEXT,
                email TEXT,
                areas_estudo LIST<TEXT>,
                PRIMARY KEY((id,pais), cidade)                            
            )
            """);
        
        self.cassandra_session.execute(query=query_create)
        pass

    def adicionar(self, aluno : Aluno):
        #---------------------------------------------------------------------Questão 1 a.
        query_insert = ("""
            INSERT INTO Aluno (id, pais, cidade, endereco, nome, email, areas_estudo) 
                VALUES (%(id)s, %(pais)s, %(cidade)s, %(endereco)s, %(nome)s, %(email)s, %(areas_estudo)s);                      
        """)

        self.cassandra_session.execute(query_insert, aluno.to_dict())
        pass

    def get_quantidade_alunos(self):
        #---------------------------------------------------------------------Questão 1 a.
        query_select = ("""
            SELECT COUNT(id) AS quantidade FROM Aluno ALLOW FILTERING;
        """)

        resultado = self.cassandra_session.execute(query_select)
        return resultado.one()['quantidade']

    def get_alunos_pais(self, pais : str):
        #---------------------------------------------------------------------Questão 2
        query_select = ("""
            SELECT * FROM Aluno WHERE pais = %s ALLOW FILTERING
        """)

        rows = self.cassandra_session.execute(query_select, [pais])

        return [Aluno(
            id=row['id'],
            pais=row['pais'],
            cidade = row['cidade'],
            endereco=row['endereco'],
            nome=row['nome'],
            email=row['email'],
            areas_estudo=list(row['areas_estudo'])
        ) for row in rows]

    def adicionar_cache(self, aluno : Aluno):
        #---------------------------------------------------------------------Questão 2
        # Adicionar no Redis

        dados = aluno.to_dict()
        dados['areas_estudo'] = ",".join(dados['areas_estudo'])
        self.redis_connection.hset(f"aluno:{aluno.id}", mapping=dados)

    def get_cache(self):
        #---------------------------------------------------------------------Questão 2
        keys = self.redis_connection.keys("aluno:*")
        alunos = []

        for key in keys:
            d = self.redis_connection.hgetall(key)
            if d:
                areas = d['areas_estudo'].split(',')
                alunos.append(Aluno(
                    id=(d['id']), pais=d['pais'], cidade=d['cidade'],
                    endereco=d['endereco'], nome=d['nome'], email=d['email'],
                    areas_estudo=areas
                ))

        return alunos

    def get_areas_estudo_cache(self, aluno_id : int):
        #---------------------------------------------------------------------Questão 3
        d = self.redis_connection.hgetall(f"aluno:{aluno_id}")
        return d['areas_estudo'].split(',')
    

    def adicionar_lista_desejos_cache(self, aluno_id : int, lista_desejos : list):
        #---------------------------------------------------------------------Questão 4
        for curso in lista_desejos:
            curso_id = curso['id']
            chave_do_curso = f'aluno:{aluno_id}:desejo:{curso_id}'
            self.redis_connection.hset(chave_do_curso, mapping=curso)

    def get_lista_desejos_cache(self, aluno_id : int):
        #---------------------------------------------------------------------Questão 4
        chaves = self.redis_connection.keys(f"aluno:{aluno_id}:desejo:*")
        lista_desejos = []
        for chave in chaves:
            curso_dados = self.redis_connection.hgetall(chave)
            if curso_dados:
                lista_desejos.append(curso_dados)
        return lista_desejos

class CursoDAO:
    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()

    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 1 b.
        query_create = ("""
            CREATE TABLE IF NOT EXISTS Curso (
                id INT,
                categoria TEXT,
                nome TEXT,
                custo_producao FLOAT,
                preco FLOAT,
                duracao_horas INT,
                PRIMARY KEY(id)                        
            );                               
        """)
        self.cassandra_session.execute(query_create)
        pass

    def adicionar(self, curso : Curso):
        #---------------------------------------------------------------------Questão 1 b.
        query_insert = ("""
            INSERT INTO Curso (id, categoria, nome, custo_producao, preco, duracao_horas)
                VALUES (%(id)s, %(categoria)s, %(nome)s,
                %(custo_producao)s, %(preco)s, %(duracao_horas)s);                
        """)
        self.cassandra_session.execute(query_insert, curso.to_dict())
        pass

    def get_custo_total(self):
        #---------------------------------------------------------------------Questão 1 b.
        query_select = ("""
            SELECT SUM(custo_producao) AS custo_total FROM Curso;                       
        """)
        resultado = self.cassandra_session.execute(query_select)
        return  resultado.one()['custo_total']

    def get_cursos_categoria(self, categoria):
        #---------------------------------------------------------------------Questão 3
        query_select = """
            SELECT * FROM Curso WHERE categoria = %s ALLOW FILTERING
        """

        rows = self.cassandra_session.execute(query_select, [categoria])

        return [Curso(
            id=row['id'],
            categoria=row['categoria'],
            nome=row['nome'],
            custo_producao=row['custo_producao'],
            preco=round(float(row['preco']), 2),
            duracao_horas=row['duracao_horas']
        ) for row in rows]

class MatriculaDAO:
    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()

    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 5
        query_create = ("""
            CREATE TABLE IF NOT EXISTS Matricula (
                id INT,
                mes INT,
                ano INT,
                hora TEXT,
                valor_total FLOAT,
                cursos_quantidade LIST<FROZEN<MAP<INT,INT>>>,
                aluno_id INT,
                PRIMARY KEY((id,ano), mes)
            );

        """)
        self.cassandra_session.execute(query_create)
        pass

    def adicionar(self, id: str, data_hora : datetime, aluno_id: int, lista_desejos : list):
        #---------------------------------------------------------------------Questão 5
        valor_total = sum(float(curso['preco']) for curso in lista_desejos)
        cursos_quantidade = [{int(curso['id']):1} for curso in lista_desejos]
        
        query_insert = """
            INSERT INTO Matricula (id, mes, ano, hora, valor_total,
                cursos_quantidade, aluno_id) VALUES (%(id)s, %(mes)s, %(ano)s,
                    %(hora)s, %(valor_total)s, %(cursos_quantidade)s,
                        %(aluno_id)s);
        """
        self.cassandra_session.execute(query_insert, {
            'id': id,
            'mes': data_hora.month,
            'ano': data_hora.year,
            'hora': data_hora.strftime("%H:%M"),
            'valor_total': valor_total,
            'cursos_quantidade': cursos_quantidade,
            'aluno_id': aluno_id
        } )

    def get_matriculas(self, data_hora : datetime):
        #---------------------------------------------------------------------Questão 5
        query_select = """
            SELECT * FROM Matricula WHERE ano = %s AND mes = %s ALLOW FILTERING

        """

        rows = self.cassandra_session.execute(query_select, [data_hora.year, data_hora.month])

        return [{
            'aluno_id': row['aluno_id'],
            'hora': row['hora'],
            'valor': round(float(row['valor_total']), 2)
        } for row in rows]
        



aluno_dao = AlunoDAO()
curso_dao = CursoDAO()
        
def test_questao_1_a():

    alunos = [
        {"id":1, "pais": "Brasil", "cidade": "São Paulo", "endereco": "Av. Paulista, 1000", "nome":"Ana Silva", "email":"ana.silva@email.com", "areas_estudo": ["programação", "web", "python", "banco de dados", "machine learning"]},
        {"id":2, "pais": "Brasil", "cidade": "Rio de Janeiro", "endereco": "Rua Copacabana, 200", "nome":"Carlos Santos", "email":"carlos.santos@email.com", "areas_estudo": ["design", "ui/ux", "frontend", "javascript", "react"]},
        {"id":3, "pais": "Argentina", "cidade": "Buenos Aires", "endereco": "Av. Corrientes, 500", "nome":"María García", "email":"maria.garcia@email.com", "areas_estudo": ["data science", "python", "estatística", "visualização", "big data"]},
        {"id":4, "pais": "Brasil", "cidade": "Belo Horizonte", "endereco": "Rua da Bahia, 300", "nome":"João Oliveira", "email":"joao.oliveira@email.com", "areas_estudo": ["mobile", "android", "kotlin", "ios", "swift"]}
    ]

    output = len(alunos)


    aluno_dao.criar_tabela()

    for aluno in alunos:
        aluno_obj = Aluno(
            id=aluno['id'],
            pais=aluno['pais'],
            cidade=aluno['cidade'],
            endereco=aluno['endereco'],
            nome=aluno['nome'],
            email=aluno['email'],
            areas_estudo=aluno['areas_estudo'],
        )
        aluno_dao.adicionar(aluno_obj)

    quantidade_alunos = aluno_dao.get_quantidade_alunos()

    assert output == quantidade_alunos

def teste_questao_1_b():
    cursos = [
        {"id":1, "categoria": "programação", "nome":"Python Avançado", "custo_producao": 5000.00, "preco": 299.90, "duracao_horas": 40},
        {"id":2, "categoria": "design", "nome":"UI/UX Design", "custo_producao": 3500.00, "preco": 199.90, "duracao_horas": 30},
        {"id":3, "categoria": "data science", "nome":"Data Science com Python", "custo_producao": 6000.00, "preco": 349.90, "duracao_horas": 50},
        {"id":4, "categoria": "mobile", "nome":"Desenvolvimento Android", "custo_producao": 4500.00, "preco": 249.90, "duracao_horas": 35},
        {"id":5, "categoria": "programação", "nome":"JavaScript Moderno", "custo_producao": 4000.00, "preco": 229.90, "duracao_horas": 32},
        {"id":6, "categoria": "design", "nome":"Figma para Iniciantes", "custo_producao": 2500.00, "preco": 149.90, "duracao_horas": 20},
        {"id":7, "categoria": "data science", "nome":"Machine Learning", "custo_producao": 7000.00, "preco": 399.90, "duracao_horas": 60},
        {"id":8, "categoria": "mobile", "nome":"Desenvolvimento iOS", "custo_producao": 5000.00, "preco": 299.90, "duracao_horas": 40}
    ]

    output = 37500.00

    curso_dao.criar_tabela()

    for curso in cursos:
        curso_obj = Curso(
            id=curso['id'],
            categoria=curso['categoria'],
            nome=curso['nome'],
            custo_producao=curso['custo_producao'],
            preco=curso['preco'],
            duracao_horas=curso['duracao_horas']
        )
        curso_dao.adicionar(curso_obj)

    custo_total = curso_dao.get_custo_total()
    
    assert output == custo_total

def test_questao_2():

    pais = "Brasil"

    output = [
        {"id":'1', "pais": "Brasil", "cidade": "São Paulo", "endereco": "Av. Paulista, 1000", "nome":"Ana Silva", "email":"ana.silva@email.com", "areas_estudo": ["programação", "web", "python", "banco de dados", "machine learning"]},
        {"id":'2', "pais": "Brasil", "cidade": "Rio de Janeiro", "endereco": "Rua Copacabana, 200", "nome":"Carlos Santos", "email":"carlos.santos@email.com", "areas_estudo": ["design", "ui/ux", "frontend", "javascript", "react"]},
        {"id":'4', "pais": "Brasil", "cidade": "Belo Horizonte", "endereco": "Rua da Bahia, 300", "nome":"João Oliveira", "email":"joao.oliveira@email.com", "areas_estudo": ["mobile", "android", "kotlin", "ios", "swift"]}
    ]

    alunos = aluno_dao.get_alunos_pais(pais)

    for aluno_obj in alunos:
        aluno_dao.adicionar_cache(aluno_obj)

    alunos_cache_dict = [aluno_cache.to_dict() for aluno_cache in aluno_dao.get_cache()]

    assert output == sorted(alunos_cache_dict, key=lambda d: d['id'])

def test_questao_3():

    aluno_id = 2

    output = [
        {"id":2, "nome":"UI/UX Design", "preco": 199.90},
        #{"id":5, "nome":"JavaScript Moderno", "preco": 229.90}, Quebra
        {"id":6, "nome":"Figma para Iniciantes", "preco": 149.90}
    ]

    areas_estudo = aluno_dao.get_areas_estudo_cache(aluno_id)
    cursos_dict = []
    for area in areas_estudo:
        cursos = curso_dao.get_cursos_categoria(area)
        for curso in cursos:
            curso_dict = {
                "id": curso.id,
                "nome": curso.nome,
                "preco": curso.preco
            }
            cursos_dict.append(curso_dict)

    assert output == sorted(cursos_dict, key=lambda d: d['id'])

def test_questao_4():

    aluno_id = 2

    lista_desejos = [
        {"id":'2', "nome":"UI/UX Design", "preco": '199.90', "duracao_horas": '30'},
        {"id":'6', "categoria": "design", "nome":"Figma para Iniciantes", "preco": '149.90', "duracao_horas": '20'},
    ]

    aluno_dao.adicionar_lista_desejos_cache(aluno_id, lista_desejos)

    lista_desejos_cache = aluno_dao.get_lista_desejos_cache(aluno_id)

    assert lista_desejos == sorted(lista_desejos_cache, key=lambda d: d["id"])

matricula_dao = MatriculaDAO()

def test_questao_5():

    aluno_id = 2
    data_hora = datetime.now()

    output = [{"aluno_id": 2, 'hora': data_hora.strftime("%H:%M"), 'valor': 349.80}]

    matricula_dao.criar_tabela()

    lista_desejos_cache = aluno_dao.get_lista_desejos_cache(aluno_id)

    matricula_dao.adicionar(1, data_hora, aluno_id, lista_desejos_cache)

    matriculas = matricula_dao.get_matriculas(data_hora)

    assert output == sorted(matriculas, key=lambda d: d["hora"])

