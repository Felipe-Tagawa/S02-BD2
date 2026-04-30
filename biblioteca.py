from pymongo import MongoClient
import pytest
from datetime import datetime


# ==============================================================================
# CONFIGURAÇÃO DO CLIENTE MONGODB
# ==============================================================================

class MongoDBClient:
    mongo_uri = "mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/"
    db_name   = "biblioteca"

    client = None
    db     = None

    @staticmethod
    def get_db():
        if not MongoDBClient.client:
            MongoDBClient.client = MongoClient(MongoDBClient.mongo_uri)
            MongoDBClient.db     = MongoDBClient.client[MongoDBClient.db_name]
            # limpa tudo antes de rodar os testes
            MongoDBClient.db["books"].drop()
            MongoDBClient.db["members"].drop()
        return MongoDBClient.db


# ==============================================================================
# MODELOS
# ==============================================================================

class Book:
    """
    Representa um livro no acervo da biblioteca.

    Atributos:
        title (str): Título do livro.
        author (str): Nome do autor.
        year (int): Ano de publicação.
        genres (list[str]): Lista de gêneros (ex.: "Ficção", "Fantasia", "Terror").
        available_copies (int): Quantidade de cópias disponíveis para empréstimo.
        rating (float): Avaliação média do livro (0.0 a 5.0).
    """
    def __init__(self, title: str, author: str, year: int,
                 genres: list[str], available_copies: int, rating: float):
        self.title            = title
        self.author           = author
        self.year             = year
        self.genres           = genres
        self.available_copies = available_copies
        self.rating           = rating

    def to_dict(self):
        return {
            "title":            self.title,
            "author":           self.author,
            "year":             self.year,
            "genres":           self.genres,
            "available_copies": self.available_copies,
            "rating":           self.rating,
        }


class Member:
    """
    Representa um membro cadastrado na biblioteca.

    Atributos:
        name (str): Nome do membro.
        email (str): E-mail do membro (identificador único).
        membership_type (str): Tipo de associação — "Básico", "Premium" ou "Estudante".
        favorite_genres (list[str]): Gêneros preferidos do membro.
        loans (list[dict]): Histórico de empréstimos, cada um com:
            - "title" (str): Título do livro.
            - "loan_date" (str): Data no formato "YYYY-MM-DD".
            - "returned" (bool): Se o livro já foi devolvido.
    """
    def __init__(self, name: str, email: str, membership_type: str,
                 favorite_genres: list[str], loans: list[dict]):
        self.name             = name
        self.email            = email
        self.membership_type  = membership_type
        self.favorite_genres  = favorite_genres
        self.loans            = loans

    def to_dict(self):
        return {
            "name":             self.name,
            "email":            self.email,
            "membership_type":  self.membership_type,
            "favorite_genres":  self.favorite_genres,
            "loans":            self.loans,
        }


# ==============================================================================
# DAOs
# ==============================================================================

class BookDAO:

    def __init__(self):
        self.db = MongoDBClient.get_db()

    def add_book(self, book: Book):
        """
        Questão 1 — (20 pts)

        Insere um livro na coleção "books".
        Se já existir um livro com o mesmo título e autor, atualiza seus dados
        em vez de duplicar (use update_one com upsert=True).
        """
        self.db['books'].update_one(
            {"title": book.title, "author": book.author},
            {"$set": book.to_dict()},
            upsert=True
        )

    def get_books_by_genre(self, genre: str) -> list[dict]:
        """
        Questão 2 — (15 pts)

        Retorna todos os livros que pertencem ao gênero informado.
        O retorno deve ser uma lista de dicionários com as chaves:
            - "title"  (str)
            - "author" (str)
            - "rating" (float)
        ordenada do maior rating para o menor
        (em caso de empate, ordenar pelo título em ordem alfabética crescente).
        """
        result = self.bd["books"].find(
            {"genres": genre},
            {"_id": 0, "title": 1, "author": 1, "rating": 1}).sort([("rating", -1), ("title", 1)])
        return list(result)

    def update_rating(self, title: str, new_rating: float):
        """
        Questão 3 — (15 pts)

        Atualiza o campo "rating" do livro com o título informado.
        Se o livro não existir, não faz nada.
        """
        self.bd["books"].update_one(
            {"title": title},
            {"$set": {"rating": new_rating}}
        )


class MemberDAO:

    def __init__(self):
        self.db = MongoDBClient.get_db()

    def add_member(self, member: Member):
        """
        Questão 4 — (20 pts)

        Insere um membro na coleção "members".
        Se já existir um membro com o mesmo email, atualiza seus dados
        (use update_one com upsert=True).

        O campo "loans" deve ser armazenado como array de subdocumentos,
        cada um com os campos: title, loan_date (como string), returned.
        """
        self.bd["members"].update_one(
            {"email": member.email},
            {"$set": member.to_dict()},
            upsert=True
        )

    def get_active_loans(self, email: str) -> list[dict]:
        """
        Questão 5 — (20 pts)

        Retorna todos os empréstimos ainda não devolvidos (returned=False)
        de um membro identificado pelo email.

        O retorno deve ser uma lista de dicionários com as chaves:
            - "title"     (str)
            - "loan_date" (str)
        ordenada pela loan_date em ordem crescente (mais antiga primeiro).
        """
        self.bd["members"].update_one(
            member = self.db["members"].find_one({"email": email})
        loans = [
            {"title": l["title"], "loan_date": l["loan_date"]}
        for l in member["loans"]
            if not l["returned"]
        ]
            return sorted(loans, key=lambda l: l["loan_date"])
        )

    def return_book(self, email: str, book_title: str):
        """
        Questão 6 — (25 pts)

        Marca como devolvido (returned=True) o empréstimo do livro com o
        título informado para o membro identificado pelo email.

        Além disso, incrementa em 1 o campo available_copies do livro
        correspondente na coleção "books".

        Se o membro ou o livro não existirem, não faz nada.
        """
        raise NotImplementedError

    def get_recommendations(self, email: str) -> list[dict]:
        """
        Questão 7 — (Bônus — 20 pts)

        Retorna até 5 recomendações de livros para o membro, com base nos
        seus gêneros favoritos (favorite_genres).

        Regras:
          - O livro deve pertencer a pelo menos um dos gêneros favoritos do membro.
          - O livro deve ter available_copies > 0.
          - O livro não pode estar nos empréstimos ativos do membro (returned=False).
          - Ordenar pelo rating decrescente; em empate, pelo título crescente.
          - Retornar no máximo 5 resultados.

        O retorno deve ser uma lista de dicionários com as chaves:
            - "title"  (str)
            - "author" (str)
            - "rating" (float)
        """
        raise NotImplementedError


# ==============================================================================
# INSTÂNCIAS GLOBAIS
# ==============================================================================

book_dao   = BookDAO()
member_dao = MemberDAO()


# ==============================================================================
# TESTES
# ==============================================================================

def test_questao_1_e_2():
    """
    Testa add_book (Questão 1) e get_books_by_genre (Questão 2).
    """

    books_data = [
        {"title": "O Nome do Vento",       "author": "Patrick Rothfuss", "year": 2007, "genres": ["Fantasia"],           "available_copies": 3, "rating": 4.8},
        {"title": "1984",                  "author": "George Orwell",    "year": 1949, "genres": ["Ficção", "Distopia"],  "available_copies": 5, "rating": 4.7},
        {"title": "Duna",                  "author": "Frank Herbert",    "year": 1965, "genres": ["Ficção", "Fantasia"],  "available_copies": 2, "rating": 4.6},
        {"title": "A Metamorfose",         "author": "Franz Kafka",      "year": 1915, "genres": ["Ficção", "Terror"],   "available_copies": 4, "rating": 4.3},
        {"title": "O Senhor dos Anéis",    "author": "J.R.R. Tolkien",  "year": 1954, "genres": ["Fantasia"],            "available_copies": 1, "rating": 4.9},
        {"title": "It: A Coisa",           "author": "Stephen King",     "year": 1986, "genres": ["Terror"],              "available_copies": 3, "rating": 4.5},
        {"title": "Admirável Mundo Novo",  "author": "Aldous Huxley",   "year": 1932, "genres": ["Ficção", "Distopia"],  "available_copies": 2, "rating": 4.4},
        {"title": "O Hobbit",              "author": "J.R.R. Tolkien",  "year": 1937, "genres": ["Fantasia"],            "available_copies": 6, "rating": 4.7},
        {"title": "O Iluminado",           "author": "Stephen King",     "year": 1977, "genres": ["Terror"],              "available_copies": 2, "rating": 4.2},
        {"title": "Fundação",              "author": "Isaac Asimov",     "year": 1951, "genres": ["Ficção"],              "available_copies": 4, "rating": 4.5},
    ]

    for bd in books_data:
        book_dao.add_book(Book(bd["title"], bd["author"], bd["year"],
                               bd["genres"], bd["available_copies"], bd["rating"]))

    # testa upsert — rodar add_book duas vezes não duplica
    book_dao.add_book(Book("1984", "George Orwell", 1949, ["Ficção", "Distopia"], 5, 4.7))
    assert MongoDBClient.get_db()["books"].count_documents({"title": "1984"}) == 1

    # --- Questão 2 ---
    expected = [
        {"title": "O Senhor dos Anéis",  "author": "J.R.R. Tolkien",  "rating": 4.9},
        {"title": "O Nome do Vento",     "author": "Patrick Rothfuss", "rating": 4.8},
        {"title": "O Hobbit",            "author": "J.R.R. Tolkien",  "rating": 4.7},
        {"title": "Duna",                "author": "Frank Herbert",    "rating": 4.6},
    ]

    output = book_dao.get_books_by_genre(genre="Fantasia")
    assert expected == output


def test_questao_3():
    """
    Testa update_rating (Questão 3).
    Depende dos dados de test_questao_1_e_2.
    """

    book_dao.update_rating(title="O Hobbit", new_rating=4.95)

    doc = MongoDBClient.get_db()["books"].find_one({"title": "O Hobbit"})
    assert doc["rating"] == 4.95

    # livro inexistente não deve lançar erro
    book_dao.update_rating(title="Livro que Não Existe", new_rating=3.0)


def test_questao_4_e_5():
    """
    Testa add_member (Questão 4) e get_active_loans (Questão 5).
    """

    members_data = [
        {
            "name": "Ana Lima",
            "email": "ana@email.com",
            "membership_type": "Premium",
            "favorite_genres": ["Fantasia", "Ficção"],
            "loans": [
                {"title": "O Nome do Vento",    "loan_date": "2024-11-01", "returned": False},
                {"title": "1984",               "loan_date": "2024-10-15", "returned": True},
                {"title": "Duna",               "loan_date": "2025-01-10", "returned": False},
            ],
        },
        {
            "name": "Bruno Souza",
            "email": "bruno@email.com",
            "membership_type": "Básico",
            "favorite_genres": ["Terror"],
            "loans": [
                {"title": "It: A Coisa",   "loan_date": "2025-02-20", "returned": False},
                {"title": "O Iluminado",   "loan_date": "2024-12-05", "returned": True},
            ],
        },
        {
            "name": "Carla Mendes",
            "email": "carla@email.com",
            "membership_type": "Estudante",
            "favorite_genres": ["Ficção", "Distopia"],
            "loans": [],
        },
    ]

    for md in members_data:
        member_dao.add_member(Member(
            md["name"], md["email"], md["membership_type"],
            md["favorite_genres"], md["loans"]
        ))

    # testa upsert
    member_dao.add_member(Member(
        "Bruno Souza", "bruno@email.com", "Básico", ["Terror"],
        [
            {"title": "It: A Coisa", "loan_date": "2025-02-20", "returned": False},
            {"title": "O Iluminado", "loan_date": "2024-12-05", "returned": True},
        ]
    ))
    assert MongoDBClient.get_db()["members"].count_documents({"email": "bruno@email.com"}) == 1

    # --- Questão 5 ---
    expected = [
        {"title": "O Nome do Vento", "loan_date": "2024-11-01"},
        {"title": "Duna",            "loan_date": "2025-01-10"},
    ]

    output = member_dao.get_active_loans(email="ana@email.com")
    assert expected == output


def test_questao_6():
    """
    Testa return_book (Questão 6).
    Depende dos dados de test_questao_4_e_5.
    """

    db = MongoDBClient.get_db()

    copies_antes = db["books"].find_one({"title": "Duna"})["available_copies"]

    member_dao.return_book(email="ana@email.com", book_title="Duna")

    # empréstimo marcado como devolvido
    member = db["members"].find_one({"email": "ana@email.com"})
    loan   = next(l for l in member["loans"] if l["title"] == "Duna")
    assert loan["returned"] is True

    # cópia incrementada
    copies_depois = db["books"].find_one({"title": "Duna"})["available_copies"]
    assert copies_depois == copies_antes + 1

    # membro inexistente não deve lançar erro
    member_dao.return_book(email="naoexiste@email.com", book_title="Duna")


def test_questao_7_bonus():
    """
    Testa get_recommendations (Questão 7 — Bônus).
    Depende dos dados de test_questao_4_e_5.

    Ana tem gêneros favoritos ["Fantasia", "Ficção"] e dois empréstimos ativos:
    "O Nome do Vento" e "Duna" (devolvido no test_questao_6, então volta a aparecer).

    Após a devolução de "Duna" no test_questao_6, os ativos de Ana são
    só "O Nome do Vento". As recomendações devem excluir esse livro
    e incluir disponíveis com copies > 0 nos gêneros dela.
    """

    output = member_dao.get_recommendations(email="ana@email.com")

    titles = [r["title"] for r in output]

    assert "O Nome do Vento" not in titles  # ainda emprestado
    assert len(output) <= 5

    # todos retornados têm available_copies > 0 (garantido pelo DAO)
    for rec in output:
        doc = MongoDBClient.get_db()["books"].find_one({"title": rec["title"]})
        assert doc["available_copies"] > 0

    # ordenação: rating desc, título asc
    ratings = [r["rating"] for r in output]
    assert ratings == sorted(ratings, reverse=True)