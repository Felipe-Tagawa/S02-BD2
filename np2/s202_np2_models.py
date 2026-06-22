class Usuario:
    def __init__(self, id, estado, cidade, endereco, nome, email, interesses):
        self.id =id
        self.estado = estado
        self.cidade = cidade
        self.endereco = endereco
        self.nome = nome
        self.email = email
        self.interesses = interesses

    def to_dict(self):
        return {
            "id": self.id,
            "estado": self.estado,
            "cidade": self.cidade,
            "endereco": self.endereco,
            "nome": self.nome,
            "email": self.email,
            "interesses": self.interesses
        }
    
class Produto:
    def __init__(self, id, categoria, nome, custo, preco, quantidade):
        self.id = id
        self.categoria = categoria
        self.nome = nome
        self.custo = custo
        self.preco = preco
        self.quantidade = quantidade

    def to_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "nome": self.nome,
            "custo": self.custo,
            "preco": self.preco,
            "quantidade": self.quantidade
        }

class Venda:
    def __init__(self, id, dia, mes, ano, hora, valor, produtos):
        self.id = id
        self.dia = dia
        self.mes = mes
        self.ano = ano
        self.hora = hora
        self.valor = valor
        self.produtos = produtos

    def to_dict(self):
        return {
            "id": self.id,
            "dia": self.dia,
            "mes": self.mes,
            "ano": self.ano,
            "hora": self.hora,
            "valor": self.valor,
            "produtos": [ p.to_dict() for p in self.produtos ]
        }
