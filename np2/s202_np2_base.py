from datetime import datetime

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

import redis

from s202_np2_models import Usuario, Produto, Venda

class CassandraDBConnector:   
    nodes = ['localhost']
    port = 9042   

    key_space = "loja" 
    
    session = None

    staticmethod
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

            CassandraDBConnector.clean_database() # TODO comment this to keep database

        return CassandraDBConnector.session
    
    staticmethod
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

    def close():
        CassandraDBConnector.session.shutdown()

class RedisDBConnector:

    redis_host = "localhost"
    redis_port = 6379

    connection = None

    staticmethod
    def get_connection():
        if RedisDBConnector.connection == None:
            RedisDBConnector.connection = redis.Redis(
                host=RedisDBConnector.redis_host, 
                port=RedisDBConnector.redis_port, 
                decode_responses=True
            )
            RedisDBConnector.connection.flushall()
        return RedisDBConnector.connection
    
    def close():
        RedisDBConnector.connection.close()
                                
class UsuarioDAO:   

    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()
        self.redis_connection = RedisDBConnector.get_connection()
    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 1 a.
        query = """
            CREATE TABLE IF NOT EXISTS Usuario (
                id INT,
                estado TEXT,
                cidade TEXT,
                endereco TEXT,
                nome TEXT,
                email TEXT,
                interesses LIST<TEXT>,
                PRIMARY KEY((estado, cidade), id)
            );
        """
        self.cassandra_session.execute(query)

        query_index = "CREATE INDEX IF NOT EXISTS usuario_estado_idx ON Usuario(estado);" # Possibilitar busca por estado sem ALLOW FILTERING
        self.cassandra_session.execute(query_index) 

    def adicionar(self, usuario : Usuario):
        #---------------------------------------------------------------------Questão 1 a.
        query = """
            INSERT INTO Usuario (id, estado, cidade, endereco, nome, email, interesses)
            VALUES (%(id)s, %(estado)s, %(cidade)s, %(endereco)s, %(nome)s, %(email)s, %(interesses)s);
        """

        self.cassandra_session.execute(query, usuario.to_dict())

    def get_quantidade_usuarios(self):
        #---------------------------------------------------------------------Questão 1 a.
        query_select = """
            SELECT COUNT(id) AS quantidade FROM Usuario ALLOW FILTERING;
        """

        result = self.cassandra_session.execute(query_select)
        return result.one()['quantidade']

    def get_usuarios_estado(self, estado : str):
        #---------------------------------------------------------------------Questão 2
        query_select = """
            SELECT * FROM Usuario WHERE estado = %(estado)s;
        """

        rows = self.cassandra_session.execute(query_select, [estado])

        lista = []
        for r in rows:
            lista.append(Usuario(
                id = r['id'],
                estado = r['estado'],
                cidade = r['cidade'],
                endereco = r['endereco'],
                nome = r['nome'],
                email = r['email'],
                interesses = list(r['interesses'])
            ))

        return lista


    def adicionar_cache(self, usuario : Usuario):
        #---------------------------------------------------------------------Questão 2
        dados = usuario.to_dict()
        dados["interesses"] = ",".join(dados["interesses"])
        self.redis_connection.hset(f"usuario:{usuario.id}", mapping = dados)

    def get_cache(self):
        #---------------------------------------------------------------------Questão 2
        keys = self.redis_connection.keys("usuario:*")
        return [Usuario(
            id = self.redis_connection.hget(keys, 'id'),
            estado = self.redis_connection.hget(keys, 'estado'),
            cidade = self.redis_connection.hget(keys, 'cidade'),
            endereco = self.redis_connection.hget(keys, 'endereco'),
            nome = self.redis_connection.hget(keys, 'nome'),
            email = self.redis_connection.hget(keys, 'email'),
            interesses = self.redis_connection.hget(keys, 'interesses').split(",")
        )]

    def get_interesses_cache(self, usuario_id : int):
        #---------------------------------------------------------------------Questão 3
        data = self.redis_connection.hgetall(f"usuario:{usuario_id}")
        return data['interesses'].split(",")

    def adicionar_carrinho_cache(self, usuario_id : int, carrinho : list):
        #---------------------------------------------------------------------Questão 4
        for produto in carrinho:
            key = f"usuario:{usuario_id}:carrinho:{produto['id']}"
            self.redis_connection.hset(key, mapping = produto)

    def get_carrinho_cache(self, usuario_id : int):
        #---------------------------------------------------------------------Questão 4
        keys = self.redis_connection.keys(f"usuario:{usuario_id}:carrinho:*")
        return [self.redis_connection.hgetall(key) for key in keys]

class ProdutoDAO:
    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()

    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 1 b.
        query = """
            CREATE TABLE IF NOT EXISTS Produto (
                id INT,
                categoria TEXT,
                nome TEXT,
                custo FLOAT,
                preco FLOAT,
                quantidade INT,
                PRIMARY KEY ((categoria), id)
            );
        """

        self.cassandra_session.execute(query)

    def adicionar(self, produto : Produto):
        #---------------------------------------------------------------------Questão 1 b.
        query = """
            INSERT INTO Produto (id, categoria, nome, custo, preco, quantidade)
            VALUES (%(id)s, %(categoria)s, %(nome)s, %(custo)s, %(preco)s, %(quantidade)s);
        """

        self.cassandra_session.execute(query, produto.to_dict())

    def get_custo_total(self):
        #---------------------------------------------------------------------Questão 1 b.
        query_select = """
            SELECT SUM(custo * quantidade) AS custo_total FROM Produto ALLOW FILTERING;
        """
        result = self.cassandra_session.execute(query_select)

        return round(result.one()['custo_total'],2) # Diferente do teste por 0.01.

    def get_produtos_categoria(self, categoria):
        #---------------------------------------------------------------------Questão 3
        query_select = """
            SELECT categoria FROM Produto ALLOW FILTERING;
        """

        return self.cassandra_session.execute(query_select, [categoria])

class VendaDAO:
    def __init__(self):
        self.cassandra_session = CassandraDBConnector.get_session()

    def criar_tabela(self):
        #---------------------------------------------------------------------Questão 5
        query = """
            CREATE TABLE IF NOT EXISTS Venda (
                id INT,
                dia INT,
                mes INT,
                ano INT,
                hora TEXT,
                valor FLOAT,
                produto_quantidade LIST<FROZEN<MAP<INT,INT>>>,
                usuario_id INT,
                PRIMARY KEY ((dia, mes, ano), hora, id)
            );
        """

        self.cassandra_session.execute(query)

    def adicionar(self, id: str, data_hora : datetime, usuario_id: int, carrinho : list):
        #---------------------------------------------------------------------Questão 5

        query = """
            INSERT INTO Venda (id, dia, mes, ano, hora, valor, produto_quantidade, usuario_id)
            VALUES (%(id)s, %(dia)s, %(mes)s, %(ano)s, %(hora)s, %(valor)s, %(produto_quantidade)s, %(usuario_id)s);
        """

        self.cassandra_session.execute(query, mapping = {
            'id': id,
            'dia': data_hora.day,
            'mes': data_hora.month,
            'ano': data_hora.year,
            'hora': data_hora.strftime("%H:%M"),
            'valor': usuario_id,
            'produto_quantidade': carrinho,
            'usuario_id': usuario_id
        })

    def get_vendas(self, data_hora : datetime):
        #---------------------------------------------------------------------Questão 5

        query_select = """
            SELECT id, hora, valor FROM Venda ALLOW FILTERING;
        """

        result = self.cassandra_session.execute(query_select, [data_hora])
        return result



usuario_dao = UsuarioDAO()
produto_dao = ProdutoDAO()
        
def test_questao_1_a():

    usuarios = [
        {"id":1, "estado": "Minas Gerais", "cidade": "Santa Rita do Sapucaí", "endereco": "Rua A, 45", "nome":"Serafim Amarantes", "email":"samarantes@g.com", "interesses": ["futebol", "pagode", "engraçado", "cerveja", "estética"]},
        {"id":2, "estado": "São Paulo", "cidade": "São Bento do Sapucaí", "endereco": "Rua B, 67", "nome":"Tamara Borges", "email":"tam_borges@g.com", "interesses": ["estética", "jiujitsu", "luta", "academia", "maquiagem"]},
        {"id":3, "estado": "Minas Gerais", "cidade": "Santa Rita do Sapucaí", "endereco": "Rua C, 84", "nome":"Ubiratã Carvalho", "email":"bira@g.com", "interesses": ["tecnologia", "hardware", "games", "culinária", "servers"]},
        {"id":4, "estado": "Minas Gerais", "cidade": "Pouso Alegre", "endereco": "Rua D, 21", "nome":"Valéria Damasco", "email":"valeria_damasco@g.com", "interesses": ["neurociências", "comportamento", "skinner", "laboratório", "pesquisa"]}
    ]

    output = len(usuarios)


    usuario_dao.criar_tabela()

    for usuario in usuarios:
        usuario_obj = Usuario(
            id=usuario['id'],
            estado=usuario['estado'],
            cidade=usuario['cidade'],
            endereco=usuario['endereco'],
            nome=usuario['nome'],
            email=usuario['email'],
            interesses=usuario['interesses'],
        )
        usuario_dao.adicionar(usuario_obj)

    quantidade_usuarios = usuario_dao.get_quantidade_usuarios()

    assert output == quantidade_usuarios

def teste_questao_1_b():
    produtos = [
        {"id":1, "categoria": "escritório", "nome":"Cadeira HM conforto", "custo": 2000.00, "preco": 3500.00, "quantidade": 120},
        {"id":2, "categoria": "culinária", "nome":"Tábua de corte Hawk", "custo": 360.00, "preco": 559.90, "quantidade": 40},
        {"id":3, "categoria": "tecnologia", "nome":"Notebook X", "custo": 3000.00, "preco": 4160.99, "quantidade": 76},
        {"id":4, "categoria": "games", "nome":"Headset W", "custo": 265.45, "preco": 422.80, "quantidade": 88},
        {"id":5, "categoria": "tecnologia", "nome":"Smartphone X", "custo": 2000.00, "preco": 3500.00, "quantidade": 120},
        {"id":6, "categoria": "games", "nome":"Gamepad Y", "custo": 256.00, "preco": 519.99, "quantidade": 40},
        {"id":7, "categoria": "estética", "nome":"Base Ismusquim", "custo": 50.00, "preco": 120.39, "quantidade": 76},
        {"id":8, "categoria": "cerveja", "nome":"Gutten Bier IPA 600ml", "custo": 65.45, "preco": 122.80, "quantidade": 88}
    ]

    output = 765559.20

    produto_dao.criar_tabela()

    for produto in produtos:
        produto_obj = Produto(
            id=produto['id'],
            categoria=produto['categoria'],
            nome=produto['nome'],
            custo=produto['custo'],
            preco=produto['preco'],
            quantidade=produto['quantidade']
        )
        produto_dao.adicionar(produto_obj)

    custo_total = produto_dao.get_custo_total()
    
    assert output == custo_total

def test_questao_2():

    estado = "Minas Gerais"

    output = [
        {"id":'1', "estado": "Minas Gerais", "cidade": "Santa Rita do Sapucaí", "endereco": "Rua A, 45", "nome":"Serafim Amarantes", "email":"samarantes@g.com", "interesses": ["futebol", "pagode", "engraçado", "cerveja", "estética"]},
        {"id":'3', "estado": "Minas Gerais", "cidade": "Santa Rita do Sapucaí", "endereco": "Rua C, 84", "nome":"Ubiratã Carvalho", "email":"bira@g.com", "interesses": ["tecnologia", "hardware", "games", "culinária", "servers"]},
        {"id":'4', "estado": "Minas Gerais", "cidade": "Pouso Alegre", "endereco": "Rua D, 21", "nome":"Valéria Damasco", "email":"valeria_damasco@g.com", "interesses": ["neurociências", "comportamento", "skinner", "laboratório", "pesquisa"]}
    ]

    usuarios = usuario_dao.get_usuarios_estado(estado)

    for usuario_obj in usuarios:
        usuario_dao.adicionar_cache(usuario_obj)

    usuarios_cache_dict = [usuario_cache.to_dict() for usuario_cache in usuario_dao.get_cache()]

    assert output == sorted(usuarios_cache_dict, key=lambda d: d['id'])

def test_questao_3():

    usuario_id = 3

    output = [
        {"id":2, "nome":"Tábua de corte Hawk", "preco": 559.90},
        {"id":3, "nome":"Notebook X", "preco": 4160.99},
        {"id":4, "nome":"Headset W", "preco": 422.80},
        {"id":5, "nome":"Smartphone X", "preco": 3500.00},
        {"id":6, "nome":"Gamepad Y", "preco": 519.99}
    ]

    interesses = usuario_dao.get_interesses_cache(usuario_id)
    produtos_dict = []
    for interesse in interesses:
        produtos = produto_dao.get_produtos_categoria(interesse)
        for produto in produtos:
            produto_dict = {
                "id": produto.id,
                "nome": produto.nome,
                "preco": produto.preco
            }
            produtos_dict.append(produto_dict)

    assert output == sorted(produtos_dict, key=lambda d: d['id'])

def test_questao_4():

    usuario_id = 3

    carrinho = [
        {"id":'4', "nome":"Headset W", "preco": '422.80', "quantidade": '1'},
        {"id":'6', "categoria": "games", "nome":"Gamepad Y", "preco": '519.99', "quantidade": '2'},
    ]

    usuario_dao.adicionar_carrinho_cache(usuario_id, carrinho)

    carrinho_cache = usuario_dao.get_carrinho_cache(usuario_id)

    assert carrinho == sorted(carrinho_cache, key=lambda d: d["id"])

venda_dao = VendaDAO()

def test_questao_5():

    usuario_id = 3
    data_hora = datetime.now()

    output = [{"usuario_id": 3, 'hora': data_hora.strftime("%H:%M"), 'valor': 1462.78}]

    venda_dao.criar_tabela()

    carrinho_cache = usuario_dao.get_carrinho_cache(usuario_id)

    venda_dao.adicionar(1, data_hora, usuario_id, carrinho_cache)

    vendas = venda_dao.get_vendas(data_hora)

    assert output == sorted(vendas, key=lambda d: d["hora"])


