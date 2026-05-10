# Cassandra RPG - Python + Cassandra com Orientação a Objetos

Projeto didático demonstrando conexão Python com Apache Cassandra usando simulação de um RPG.

## Estrutura do Banco de Dados

O projeto usa os seguintes keyspaces e tabelas:

### Keyspace: rpg_db
- **personagens**: Armazena dados dos personagens (jogadores e inimigos)
- **classes**: Define as classes disponíveis no jogo (Guerreiro, Mago, Ladino, etc.)
- **itens**: Catálogo de itens do jogo
- **inventario**: Relacionamento entre personagens e seus itens
- **missoes**: Missões disponíveis no jogo
- **missoes_personagens**: Rastreia o progresso de missões por personagem
- **batalhas**: Histórico de batalhas

## Como Executar

### 1. Instalar Dependências

```bash
pip install cassandra-driver
```

### 2. Configurar Cassandra

**Opção A - Usar Docker (Recomendado):**

```bash
docker-compose up -d
```

**Opção B - Cassandra Local:**

Certifique-se de que o Cassandra está rodando em `localhost:9042`

### 3. Executar o Projeto

```bash
python cassandra_rpg.py
```

## Conceitos Demonstrados

- ✅ Conexão com Cassandra usando Python Driver
- ✅ Criação de Keyspace e Tabelas
- ✅ Operações CRUD (Create, Read, Update, Delete)
- ✅ Consultas com CQL (Cassandra Query Language)
- ✅ Orientação a Objetos no Python
- ✅ Mapeamento Objeto-Relacional (Simplificado)
- ✅ Batch Operations
- ✅ Consistency Levels

## Classes do Projeto

### DatabaseConnection
Gerencia a conexão com o Cassandra.

### Personagem
Representa um personagem do jogo com atributos e métodos.

### GerenciadorPersonagens
CRUD completo de personagens no banco.

### Item
Itens do jogo (armas, armaduras, poções).

### GerenciadorItens
Gerenciamento de itens e inventário.

### Missao
Missões que os personagens podem completar.

### GerenciadorMissoes
Sistema de missões e progresso.

### SistemaBatalha
Simulação de batalhas entre personagens.

## Exemplo de Uso

```python
# Criar um personagem
heroi = GerenciadorPersonagens.criar_personagem(
    nome="Aragorn",
    classe="Guerreiro",
    nivel=5,
    vida=100,
    forca=15,
    destreza=10,
    inteligencia=8
)

# Equipar um item
GerenciadorItens.adicionar_item_inventario(heroi.id, "Espada Longa")

# Aceitar uma missão
GerenciadorMissoes.aceitar_missao(heroi.id, "Derrotar o Dragão")

# Batalhar
SistemaBatalha.batalhar(heroi.id, inimigo.id)
```

## Autores

Projeto criado para fins educacionais - Demonstração de Python + Cassandra + OO
