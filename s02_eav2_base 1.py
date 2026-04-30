from neo4j import GraphDatabase
import pytest
from datetime import date


# ==============================================================================
# CONFIGURAÇÃO DO DRIVER NEO4J
# ==============================================================================

class Neo4jDriver:
    neo4j_host     = "neo4j+s://e0a8d3c6.databases.neo4j.io" 
    neo4j_user     = "e0a8d3c6"                  
    neo4j_password = "gNge1VZqlYQZQQ165Qn1Gda2copk4s8eelbW6lSuBEM"              

    driver = None

    @staticmethod
    def get_driver():
        if not Neo4jDriver.driver:
            Neo4jDriver.driver = GraphDatabase.driver(
                Neo4jDriver.neo4j_host,
                auth=(Neo4jDriver.neo4j_user, Neo4jDriver.neo4j_password)
            )
            Neo4jDriver.driver.execute_query("MATCH (n) DETACH DELETE n")
        return Neo4jDriver.driver


# ==============================================================================
# MODELOS
# ==============================================================================

class Guild:
    """
    Representa uma guilda de aventureiros.

    Atributos:
        name (str): Nome da guilda.
        description (str): Descrição da guilda.
        headquarters (str): Cidade-sede da guilda.
        specializations (list[str]): Lista de especializações da guilda
            (ex.: "Combate", "Magia", "Furtividade", "Exploração", "Comércio").
    """
    def __init__(self, name: str, description: str, headquarters: str, specializations: list[str]):
        self.name            = name
        self.description     = description
        self.headquarters    = headquarters
        self.specializations = specializations

    def to_dict(self):
        return {
            "name":            self.name,
            "description":     self.description,
            "headquarters":    self.headquarters,
            "specializations": self.specializations,
        }


class Adventurer:
    """
    Representa um aventureiro que pode ser membro de uma ou mais guildas.

    Atributos:
        name (str): Nome do aventureiro.
        age (int): Idade do aventureiro.
        skills (list[str]): Lista de habilidades do aventureiro.
        rank (str): Rank do aventureiro dentro do sistema de guildas.
            Valores possíveis: "Novato", "Aprendiz", "Veterano", "Mestre", "Lendário".
        origin (str): Cidade de origem do aventureiro.
        guild_memberships (list[str]): Lista com os nomes das guildas às quais o aventureiro pertence.
        registration_date (str): Data de registro no formato "YYYY-MM-DD".
    """
    def __init__(self, name: str, age: int, skills: list[str], rank: str,
                 origin: str, guild_memberships: list[str], registration_date: str):
        self.name              = name
        self.age               = age
        self.skills            = skills
        self.rank              = rank
        self.origin            = origin
        self.guild_memberships = guild_memberships
        self.registration_date = registration_date

    def to_dict(self):
        return {
            "name":              self.name,
            "age":               self.age,
            "skills":            self.skills,
            "rank":              self.rank,
            "origin":            self.origin,
            "guild_memberships": self.guild_memberships,
            "registration_date": self.registration_date,
        }


class Quest:
    """
    Representa uma missão que pode ser aceita por aventureiros de guildas específicas.

    Atributos:
        title (str): Título da missão.
        description (str): Descrição da missão.
        reward (int): Recompensa em moedas de ouro.
        danger_level (int): Nível de perigo de 1 (baixo) a 5 (extremo).
        required_specializations (list[str]): Especializações de guilda necessárias para aceitar a missão.
        required_ranks (list[str]): Ranks mínimos aceitos para a missão.
    """
    def __init__(self, title: str, description: str, reward: int,
                 danger_level: int, required_specializations: list[str], required_ranks: list[str]):
        self.title                    = title
        self.description              = description
        self.reward                   = reward
        self.danger_level             = danger_level
        self.required_specializations = required_specializations
        self.required_ranks           = required_ranks

    def to_dict(self):
        return {
            "title":                    self.title,
            "description":              self.description,
            "reward":                   self.reward,
            "danger_level":             self.danger_level,
            "required_specializations": self.required_specializations,
            "required_ranks":           self.required_ranks,
        }


# ==============================================================================
# DAOs
# ==============================================================================

class GuildDAO:

    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    def add_guild(self, guild: Guild):
        """
        Questão 1 — (25 pts)

        Insere uma guilda no Neo4j com seus atributos (name, description, headquarters)
        e cria nós do tipo :Specialization para cada especialização da guilda,
        relacionando-os com (:Guild)-[:HAS_SPECIALIZATION]->(:Specialization).

        Use MERGE tanto para a guilda quanto para cada especialização, a fim de evitar
        duplicações quando mais de uma guilda compartilhar a mesma especialização.
        """

        query = """
            MERGE (g:Guild {name: $name})
            SET g.description = $description,
                g.headquarters = $headquarters
            FOREACH (spec_name IN $specializations |
                MERGE (s:Specialization {name: spec_name})
                MERGE (g)-[:HAS_SPECIALIZATION]->(s)
            )
        """

        data = guild.to_dict()

        self.driver.execute_query(query, **data)
        """ Outra forma de fazer:
        self.driver.execute_query(
            query,
            name=guild.name,
            description=guild.description,
            headquarters=guild.headquarters,
            specializations=guild.specializations,
        )"""

    def get_guilds_by_specialization(self, specialization: str) -> list[dict]:
        """
        Questão 2 — (15 pts)

        Retorna todas as guildas que possuem a especialização informada.
        O retorno deve ser uma lista de dicionários com as chaves:
            - "name"         (str)
            - "headquarters" (str)
        ordenada alfabeticamente pelo nome da guilda.
        """

        query = """
            MATCH(g:Guild)-[:HAS_SPECIALIZATION]->(s:Specialization {name: $specialization})
            RETURN g.name AS name, g.headquarters AS headquarters
            ORDER BY g.name
        """

        result = self.driver.execute_query(query, specialization=specialization)
        return [{"name": r["name"], "headquarters": r["headquarters"]} for r in result.records]

class AdventurerDAO:

    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    def add_adventurer(self, adventurer: Adventurer):
        """
        Questão 3 — (25 pts)

        Insere um aventureiro no Neo4j com todos os seus atributos
        (name, age, skills, rank, origin, registration_date armazenada como DATE).

        Cria relacionamentos (:Adventurer)-[:MEMBER_OF]->(:Guild) para cada guilda
        em guild_memberships. Use MERGE na Guild para não duplicar guildas já existentes.
        """

        query = """
            MERGE (a:Adventurer {name: $name})
            SET a.age = $age,
                a.skills = $skills,
                a.rank = $rank,
                a.origin = $origin,
                a.registration_date = date($registration_date)
            FOREACH (guild_name IN $guild_memberships |
                MERGE (g:Guild {name: guild_name})
                MERGE (a)-[:MEMBER_OF]->(g)
            )
        """

        data = adventurer.to_dict()

        self.driver.execute_query(query, **data)

        """ Outra forma de fazer:
        result = self.driver.execute_query(
            query,
            name=adventurer.name,
            age=adventurer.age,
            skills=adventurer.skills,
            rank=adventurer.rank,
            origin=adventurer.origin,
            guild_memberships=adventurer.guild_memberships,
            registration_date=adventurer.registration_date,
        )"""

    def get_available_quests(self, adventurer_name: str) -> list[dict]:
        """
        Questão 4 — (35 pts)

        Retorna todas as missões disponíveis para um determinado aventureiro.

        Uma missão está disponível para o aventureiro se:
          1. O rank do aventureiro está na lista required_ranks da missão, E
          2. Pelo menos uma das especializações das guildas do aventureiro
             está na lista required_specializations da missão.

        O retorno deve ser uma lista de dicionários com as chaves:
            - "title"        (str)
            - "reward"       (int)
            - "danger_level" (int)
        sem duplicatas, ordenada do maior reward para o menor
        (em caso de empate, ordenar pelo título em ordem alfabética crescente).
        """

        query = """

                MATCH (a:Adventurer {name: $adventurer_name})-[:MEMBER_OF]->(g:Guild)-[:HAS_SPECIALIZATION]->(s:Specialization)
                MATCH (q:Quest)
                WHERE a.rank IN q.required_ranks AND s.name IN q.required_specializations
                RETURN DISTINCT q.title AS title, q.reward AS reward, q.danger_level AS danger_level
                ORDER BY q.reward DESC, q.title ASC
        """

        result = self.driver.execute_query(query, adventurer_name=adventurer_name)
        return [{"title": r["title"], "reward": r["reward"], "danger_level": r["danger_level"]} for r in result.records]


    def promote_adventurer(self, adventurer_name: str, new_rank: str, new_skill: str):
        """
        Questão 5 — (20 pts)

        Atualiza o rank de um aventureiro para new_rank e acrescenta new_skill
        à lista de habilidades existente (sem apagar as habilidades anteriores).
        """

        query = """
            MATCH (a:Adventurer {name: $adventurer_name})
            SET a.rank = $new_rank,
                a.skills = a.skills + [$new_skill]
        """

        self.driver.execute_query(query, adventurer_name=adventurer_name, new_rank=new_rank, new_skill=new_skill)

class QuestDAO:

    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    def add_quest(self, quest: Quest):
        """
        Questão 1 (parte) — ver enunciado completo no método add_guild.

        Insere uma missão no Neo4j com todos os seus atributos
        (title, description, reward, danger_level, required_specializations, required_ranks).

        Armazene required_specializations e required_ranks diretamente como
        propriedades de lista no nó :Quest (não é necessário criar nós separados).
        """

        query = """
            MERGE (q:Quest {title: $title})
            SET q.description = $description,
                q.reward = $reward,
                q.danger_level = $danger_level,
                q.required_specializations = $required_specializations,
                q.required_ranks = $required_ranks
        """

        data = quest.to_dict()

        self.driver.execute_query(query, **data)
        """Outra forma de fazer
        self.driver.execute_query(query, title=quest.title, description=quest.description, reward=quest.reward,
                                   danger_level=quest.danger_level, required_specializations=quest.required_specializations, required_ranks=quest.required_ranks)
        """

    def delete_quest(self, title: str):
        """
        Questão 6 — (20 pts)

        Remove permanentemente do Neo4j a missão com o título informado,
        incluindo todos os seus relacionamentos (use DETACH DELETE).
        Se não existir nenhuma missão com esse título, não faz nada.
        """
        query = """
        MATCH (q:Quest {title: $title})
        DETACH DELETE q
        """

        self.driver.execute_query(query, title=title)


# ==============================================================================
# INSTÂNCIAS GLOBAIS (reutilizadas pelos testes)
# ==============================================================================

guild_dao      = GuildDAO()
adventurer_dao = AdventurerDAO()
quest_dao      = QuestDAO()


# ==============================================================================
# TESTES
# ==============================================================================

def test_questao_1_e_2():
    """
    Testa add_guild (Questão 1) e get_guilds_by_specialization (Questão 2).
    """

    guilds_data = [
        {
            "name": "Ordem da Chama",
            "description": "Guilda de elite focada em combate mágico e controle arcano.",
            "headquarters": "Heroica",
            "specializations": ["Combate", "Magia"],
        },
        {
            "name": "Irmandade das Sombras",
            "description": "Coletivo de espiões, ladrões e assassinos que operam nas entrelinhas.",
            "headquarters": "Uanteji",
            "specializations": ["Furtividade", "Comércio"],
        },
        {
            "name": "Companhia do Horizonte",
            "description": "Exploradores e cartógrafos que mapeiam regiões desconhecidas.",
            "headquarters": "Portoeste",
            "specializations": ["Exploração", "Combate"],
        },
        {
            "name": "Liga Mercante do Sul",
            "description": "Rede de comerciantes que controla rotas fluviais e marítimas.",
            "headquarters": "Portoeste",
            "specializations": ["Comércio", "Exploração"],
        },
        {
            "name": "Forjadores de Ferro",
            "description": "Artesãos e guerreiros das montanhas, especialistas em armamentos.",
            "headquarters": "Montanha Forja",
            "specializations": ["Combate", "Comércio"],
        },
        {
            "name": "Círculo Arcano",
            "description": "Estudiosos da magia que preservam o conhecimento arcano dos Eron.",
            "headquarters": "Cidade Cinza",
            "specializations": ["Magia", "Exploração"],
        },
        {
            "name": "Caçadores do Vale",
            "description": "Rastreadores e caçadores que patrulham o Vale da Morte.",
            "headquarters": "Vale da Morte",
            "specializations": ["Furtividade", "Exploração"],
        },
        {
            "name": "Escudeiros de Heroica",
            "description": "Ordem militar guardiã do Culto do Herói e de Heroica.",
            "headquarters": "Heroica",
            "specializations": ["Combate", "Magia"],
        },
    ]

    for gd in guilds_data:
        guild_dao.add_guild(Guild(gd["name"], gd["description"], gd["headquarters"], gd["specializations"]))

    # --- Questão 2 ---
    input_specialization = "Combate"
    expected = [
        {"name": "Companhia do Horizonte", "headquarters": "Portoeste"},
        {"name": "Escudeiros de Heroica",  "headquarters": "Heroica"},
        {"name": "Forjadores de Ferro",    "headquarters": "Montanha Forja"},
        {"name": "Ordem da Chama",         "headquarters": "Heroica"},
    ]

    output = guild_dao.get_guilds_by_specialization(specialization=input_specialization)

    assert expected == output


def test_questao_3_e_4():
    """
    Testa add_adventurer (Questão 3) e get_available_quests (Questão 4).
    Depende dos dados inseridos em test_questao_1_e_2.
    """

    quests_data = [
        {
            "title": "A Ameaça das Sombras",
            "description": "Infiltre-se na organização Uanteji e descubra seus planos secretos.",
            "reward": 800,
            "danger_level": 4,
            "required_specializations": ["Furtividade"],
            "required_ranks": ["Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Caravana Perdida",
            "description": "Escorte uma caravana de mercadores até Portoeste com segurança.",
            "reward": 200,
            "danger_level": 2,
            "required_specializations": ["Combate", "Comércio"],
            "required_ranks": ["Novato", "Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Segredos da Cidade Cinza",
            "description": "Explore as ruínas da Cidade Cinza em busca de artefatos arcanos.",
            "reward": 600,
            "danger_level": 3,
            "required_specializations": ["Magia", "Exploração"],
            "required_ranks": ["Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "O Monstro do Vale",
            "description": "Elimine a criatura sombria que aterroriza os arredores do Vale da Morte.",
            "reward": 1000,
            "danger_level": 5,
            "required_specializations": ["Furtividade", "Combate"],
            "required_ranks": ["Mestre", "Lendário"],
        },
        {
            "title": "Rota dos Cem Rios",
            "description": "Navegue pelas rotas fluviais dos Nomi coletando informações comerciais.",
            "reward": 350,
            "danger_level": 2,
            "required_specializations": ["Comércio", "Exploração"],
            "required_ranks": ["Novato", "Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Defesa de Heroica",
            "description": "Ajude os Escudeiros a repelir um ataque inimigo à cidade de Heroica.",
            "reward": 750,
            "danger_level": 4,
            "required_specializations": ["Combate", "Magia"],
            "required_ranks": ["Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Forja Maldita",
            "description": "Investigue rumores sobre uma forja amaldiçoada nas montanhas do noroeste.",
            "reward": 500,
            "danger_level": 3,
            "required_specializations": ["Magia", "Combate"],
            "required_ranks": ["Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Mapa do Tesouro",
            "description": "Siga as pistas de um antigo mapa e encontre o tesouro dos Eron.",
            "reward": 1200,
            "danger_level": 5,
            "required_specializations": ["Exploração", "Magia"],
            "required_ranks": ["Mestre", "Lendário"],
        },
        {
            "title": "Contrabando no Porto",
            "description": "Identifique e desmantele uma rede de contrabandistas em Portoeste.",
            "reward": 400,
            "danger_level": 3,
            "required_specializations": ["Furtividade", "Comércio"],
            "required_ranks": ["Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
        {
            "title": "Ervas Raras",
            "description": "Colete ervas medicinais raras nas florestas do centro-oeste.",
            "reward": 150,
            "danger_level": 1,
            "required_specializations": ["Exploração"],
            "required_ranks": ["Novato", "Aprendiz", "Veterano", "Mestre", "Lendário"],
        },
    ]

    adventurers_data = [
        {
            "name": "Draven Ashford",
            "age": 34,
            "skills": ["Esgrima", "Tiro com arco", "Rastreamento"],
            "rank": "Veterano",
            "origin": "Portoeste",
            "guild_memberships": ["Companhia do Horizonte", "Forjadores de Ferro"],
            "registration_date": "2023-03-15",
        },
        {
            "name": "Lyra Nightwhisper",
            "age": 27,
            "skills": ["Magia de ilusão", "Stealth", "Venenos"],
            "rank": "Mestre",
            "origin": "Uanteji",
            "guild_memberships": ["Irmandade das Sombras", "Caçadores do Vale"],
            "registration_date": "2022-07-20",
        },
        {
            "name": "Theron Brightblade",
            "age": 42,
            "skills": ["Combate com espada", "Liderança", "Táticas militares"],
            "rank": "Lendário",
            "origin": "Heroica",
            "guild_memberships": ["Escudeiros de Heroica", "Ordem da Chama"],
            "registration_date": "2018-01-10",
        },
        {
            "name": "Mira Stoneforge",
            "age": 55,
            "skills": ["Forjamento", "Avaliação de armas", "Negociação"],
            "rank": "Mestre",
            "origin": "Montanha Forja",
            "guild_memberships": ["Forjadores de Ferro", "Liga Mercante do Sul"],
            "registration_date": "2019-11-05",
        },
        {
            "name": "Callum Driftwood",
            "age": 22,
            "skills": ["Navegação", "Cartografia", "Escalada"],
            "rank": "Novato",
            "origin": "Portoeste",
            "guild_memberships": ["Liga Mercante do Sul"],
            "registration_date": "2025-06-01",
        },
        {
            "name": "Seraphina Voss",
            "age": 310,
            "skills": ["Magia arcana avançada", "Invocação", "Estudo de ruínas"],
            "rank": "Lendário",
            "origin": "Cidade Cinza",
            "guild_memberships": ["Círculo Arcano", "Ordem da Chama"],
            "registration_date": "2010-04-18",
        },
    ]

    for qd in quests_data:
        quest_dao.add_quest(Quest(
            qd["title"], qd["description"], qd["reward"],
            qd["danger_level"], qd["required_specializations"], qd["required_ranks"]
        ))

    for ad in adventurers_data:
        adventurer_dao.add_adventurer(Adventurer(
            ad["name"], ad["age"], ad["skills"], ad["rank"],
            ad["origin"], ad["guild_memberships"], ad["registration_date"]
        ))

    # --- Questão 4 ---
    input_adventurer_name = "Draven Ashford"
    expected = [
        {"title": "Defesa de Heroica",         "reward": 750, "danger_level": 4},
        {"title": "Segredos da Cidade Cinza",   "reward": 600, "danger_level": 3},
        {"title": "Forja Maldita",              "reward": 500, "danger_level": 3},
        {"title": "Contrabando no Porto",       "reward": 400, "danger_level": 3},
        {"title": "Rota dos Cem Rios",          "reward": 350, "danger_level": 2},
        {"title": "Caravana Perdida",           "reward": 200, "danger_level": 2},
        {"title": "Ervas Raras",                "reward": 150, "danger_level": 1},
    ]

    output = adventurer_dao.get_available_quests(adventurer_name=input_adventurer_name)

    assert expected == output


def test_questao_5():
    """
    Testa promote_adventurer (Questão 5).
    Depende dos dados inseridos em test_questao_3_e_4.

    Promove Callum Driftwood de "Novato" para "Aprendiz" e adiciona
    a habilidade "Negociação fluvial". Verifica o novo rank e que a nova
    habilidade foi acrescentada sem perder as anteriores.
    """

    input_name      = "Callum Driftwood"
    input_new_rank  = "Aprendiz"
    input_new_skill = "Negociação fluvial"

    adventurer_dao.promote_adventurer(
        adventurer_name=input_name,
        new_rank=input_new_rank,
        new_skill=input_new_skill,
    )

    result = Neo4jDriver.get_driver().execute_query(
        "MATCH (a:Adventurer {name: $name}) RETURN a.rank AS rank, a.skills AS skills",
        name=input_name,
    )

    row = result.records[0]
    assert row["rank"] == input_new_rank
    assert input_new_skill in row["skills"]
    # Habilidades anteriores preservadas
    assert "Navegação"   in row["skills"]
    assert "Cartografia" in row["skills"]
    assert "Escalada"    in row["skills"]


def test_questao_6():
    """
    Testa delete_quest (Questão 6).
    Depende dos dados inseridos em test_questao_3_e_4.

    Remove a missão "Ervas Raras" e verifica que:
      1. Ela deixa de aparecer na lista de missões disponíveis de Draven Ashford.
      2. As demais missões disponíveis para ele permanecem inalteradas.

    Em seguida remove "Caravana Perdida" e verifica o mesmo padrão.
    """

    # --- Remove "Ervas Raras" ---
    quest_dao.delete_quest(title="Ervas Raras")

    output_after_first = adventurer_dao.get_available_quests(adventurer_name="Draven Ashford")
    titles_after_first = [q["title"] for q in output_after_first]

    assert "Ervas Raras" not in titles_after_first
    assert len(output_after_first) == 6

    # --- Remove "Caravana Perdida" ---
    quest_dao.delete_quest(title="Caravana Perdida")

    output_after_second = adventurer_dao.get_available_quests(adventurer_name="Draven Ashford")
    titles_after_second = [q["title"] for q in output_after_second]

    assert "Caravana Perdida" not in titles_after_second
    assert len(output_after_second) == 5

    expected_remaining = [
        {"title": "Defesa de Heroica",        "reward": 750, "danger_level": 4},
        {"title": "Segredos da Cidade Cinza", "reward": 600, "danger_level": 3},
        {"title": "Forja Maldita",            "reward": 500, "danger_level": 3},
        {"title": "Contrabando no Porto",     "reward": 400, "danger_level": 3},
        {"title": "Rota dos Cem Rios",        "reward": 350, "danger_level": 2},
    ]

    assert expected_remaining == output_after_second

""" main não necessária se usado pytest.

def main():

    print("Testando questões 1 e 2...")
    test_questao_1_e_2()
    print("Testando questões 3 e 4...")
    test_questao_3_e_4()
    print("Testando questão 5...")
    test_questao_5()
    print("Testando questão 6...")
    test_questao_6()

if __name__ == "__main__":
    main()

"""



