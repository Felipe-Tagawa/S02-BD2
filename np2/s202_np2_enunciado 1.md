# NP2

Nessa atividade você deve usar seus conhecimentos sobre banco de dados baseados em colunas e chave-valor, mais especificamente sobre Cassandra e Redis para atender os requisitos pedidos.
Todos as questões têm um exemplo de caso de teste (com dados de entrada e saída esperada) para que você valide a sua solução.

_Construa os métodos das classes de acesso aos dados (DAO) de acordo com a descrição das questões e com base na implementaçõa de cada caso de teste._

**Contexto**: Imagine que você está desenvolvendo um banco de dados para uma loja online. Essa loja tem um volume muito grande de vendas e por isso foram escolhidos sistemas de gerenciamento de bancos de dados NoSQL. Os principais objetivos do sistema são:

i. cadastrar usuários e manter um registros de suas preferências ao longo do tempo;
ii. cadastrar produtos e suas categorias;
iii. exibir uma lista de produtos mais recomendados para um determinado usuário;
iv. armazenar temporariamente as informações de produtos no carrinho;
v. e registrar as informações de uma venda efetivada.

Para manter as informações das vendas realizadas de forma persistente e distribuída, a tabela de vendas, produtos e usuários foram registrados no Cassandra.
Apesar de ter um esquema flexível, considere as seguintes informações:

- Usuário (id: int, estado: text, cidade: text, endereço: text, nome: text, email: text, interesses: list<text>)
- Produto (id: int, categoria: text, nome: text, custo: float, preco: float, quantidade: int)
- Venda (id: int, dia: int, mês: int, ano: int, hora: text, valor: float, produto_quantidade: list<map<int, int>>, usuario_id: int)

Os donos da loja querem manter os dados de usuários de um mesmo estado e cidade juntos no banco de dados para facilitar a busca, usando o id para complementar. Produtos devem ser agrupadors por categoria, também usando id para ordenar os produtos em uma mesma partição. Por fim, os dados das vendas devem ser particionados por dia, mês e ano, usando a hora e o id para complementar a idenficação de uma venda.

A fim de manter consultas rápidas, algumas informações do usuário, suas preferências e seus produtos em carrinho são mantidas no Redis.

**Questão 1** Crie as tabelas de usuários e produtos e registe as informações no Cassandra. Em seguida realize as consultas que retornem:

a. **(20 pontos)** a quantidade de usuários registrados;
b. **(20 pontos)** e o custo total dos produtos em estoque (obs.: o custo registrado é apenas o custo unitário de cada produto).

**Questão 2 (30 pontos)** Carregue do Cassandra as informações de cada um dos usuários do estado de Minas Gerais, incluindo a lista de interesses, registre no Redis e realize a consutla no Redis para apresentar os dados registrados.

**Questão 3 (10 pontos extras)** Considere que o usuário 3 acessa o feed dele. Use a lista de interesses desse usuário registrada no Redis para buscar as informações sobre produtos mais interessantes no Cassandra (considere que a lista de interesses contém os nomes das categorias de produtos interessantes).

**Questão 4 (10 pontos extras)** Considere que o usuário 3 seleciona alguns produtos para o seu carrinho. Registre essas informações no Redis e realize uma consulta para mostrar os dados cadastrados.

**Questão 5 (10 pontos extras)** Crie a tabela de vendas no Cassandra. Considere que o usuário 3 efetiva a compra dos produtos em seu carrinho. Realize uma consulta no Redis dos dados do carrinho desse usuário e registre as informações sobre essa venda no Cassandra. Por fim, recupere os dados de todas as vendas no Cassandra.

> PS.: Todos os pontos extras podem ser aplicados na NP1 caso ultrapasse o limite de 100 pontos da NP2.
