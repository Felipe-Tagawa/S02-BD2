# [S202] EAV5

Nessa atividade você deve usar seus conhecimentos sobre banco de dados chave-valor, mais especificamente sobre Redis para atender os requisitos pedidos.
Todos as questões tem um exemplo de caso de teste (com dados de entrada e saída esperada) para que você valide a sua solução.

**Contexto**: Imagine que você está desenvolvendo um banco de dados de cache para uma rede social. O objetivo do sistema é sempre exibir os posts mais recentes dessa rede social em ordem de interesse.
Para isso, são mantidas informações sobre os interesses dos usuários e sobre o tópico de cada postagem.
Esse sistema deve armazenar o perfil de cada usuário, contendo o nome, o e-mail e um token de sessão. Além, disso o sistema deve manter uma lista de interesses para cada usuário, ordenando pelo score de interesse.
Por fim, o sistema deve manter informações sobre os posts, como id, conteúdo, e-mail do autor e data e hora de publicação. É registrado também uma lista de palavras chave sobre o post. Apenas as informações dos posts mais recentes devem ser mantidos no banco de dados (posts com mais de 5 horas devem ser excluídos).
Considere que o interesse de um usuário por um post específico é a soma dos scores de cada interesse que está presente nas palavras chave desse post específico.

### Configuração

Coloque todos os arquivos em uma mesma pasta.

Crie um ambiente virtual se achar necessário e execute o seguinte comando para instalar as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

Para executar os testes use o comando:

```bash
pytest s202_eav5_base.py
```

**Questão 1 (5 pontos)**

Registe as informações dos usuários informadas nos casos de teste e realize a consutla para apresentar os dados.

**Questão 2 (5 pontos)**

Registre uma lista de interesses para cada um dos usuários e realize a consutla para apresentar os dados.

**Questão 3 (5 pontos)**

Resgistre as informações sobre os posts mais recentes e realize a consutla para apresentar os dados.

**Questão 4 (5 pontos extras)**

Considere que o usuário 3 acessou o seu feed. Realize uma consulta nos dados cadatrados para mostrar a lista dos posts mais interessantes para esse usuário.

**Questão 5 (5 pontos extras)**

Considere que será mantido também um lista de posts já vistos por um determinado usuário. Registre essa lista para cada um dos usuários e realize a consutla para apresentar os dados.
