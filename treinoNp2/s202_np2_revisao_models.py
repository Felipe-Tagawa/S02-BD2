class Aluno:
    def __init__(self, id, pais, cidade, endereco, nome, email, areas_estudo):
        self.id = id
        self.pais = pais
        self.cidade = cidade
        self.endereco = endereco
        self.nome = nome
        self.email = email
        self.areas_estudo = areas_estudo

    def to_dict(self):
        return {
            "id": self.id,
            "pais": self.pais,
            "cidade": self.cidade,
            "endereco": self.endereco,
            "nome": self.nome,
            "email": self.email,
            "areas_estudo": self.areas_estudo
        }
    
class Curso:
    def __init__(self, id, categoria, nome, custo_producao, preco, duracao_horas):
        self.id = id
        self.categoria = categoria
        self.nome = nome
        self.custo_producao = custo_producao
        self.preco = preco
        self.duracao_horas = duracao_horas

    def to_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "nome": self.nome,
            "custo_producao": self.custo_producao,
            "preco": self.preco,
            "duracao_horas": self.duracao_horas
        }

class Matricula:
    def __init__(self, id, dia, mes, ano, hora, valor_total, cursos):
        self.id = id
        self.dia = dia
        self.mes = mes
        self.ano = ano
        self.hora = hora
        self.valor_total = valor_total
        self.cursos = cursos

    def to_dict(self):
        return {
            "id": self.id,
            "dia": self.dia,
            "mes": self.mes,
            "ano": self.ano,
            "hora": self.hora,
            "valor_total": self.valor_total,
            "cursos": [ c.to_dict() for c in self.cursos ]
        }

