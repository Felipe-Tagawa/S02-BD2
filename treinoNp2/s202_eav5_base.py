import redis

redis_conn = redis.Redis(
    host="localhost", port=6379,
    decode_responses=True
)

redis_conn.flushall()

# Questão 1
def questao_1(users):
    for user in users:
        redis_conn.hset(f"usuario:{user['id']}", mapping=user)
    
    user_keys = redis_conn.keys("usuario:*")

    return [redis_conn.hgetall(key) for key in user_keys]

def test_questao_1():

    input = [
        {"id":'1', "nome":"Serafim Amarantes", "email":"samarantes@g.com"},
        {"id":'2', "nome":"Tamara Borges", "email":"tam_borges@g.com"},
        {"id":'3', "nome":"Ubiratã Carvalho", "email":"bira@g.com"},
        {"id":'4', "nome":"Valéria Damasco", "email":"valeria_damasco@g.com"}
    ]

    assert input == sorted(questao_1(input), key=lambda d: d['id'])

# Questão 2
def questao_2(interests):
    for interest in interests:
        for item in interest['interesses']:
            redis_conn.zadd(f"usuario:{interest['usuario']}:interesses", item)

    return [redis_conn.zrange(f"usuario:{interest['usuario']}:interesses", 0, -1, withscores=True) for interest in interests]

def test_questao_2():

    input = [
        {"usuario":1, "interesses": [{"futebol":0.855}, {"pagode":0.765}, {"engraçado":0.732}, {"cerveja":0.622}, {"estética":0.519}]},
        {"usuario":2, "interesses": [{"estética":0.765}, {"jiujitsu":0.921}, {"luta":0.884}, {"academia":0.541}, {"maquiagem":0.658}]},
        {"usuario":3, "interesses": [{"tecnologia":0.999}, {"hardware":0.865}, {"games":0.745}, {"culinária":0.658}, {"servers":0.54}]},
        {"usuario":4, "interesses": [{"neurociências":0.865}, {"comportamento":0.844}, {"skinner":0.854}, {"laboratório":0.354}, {"pesquisa":0.428}]}
    ]

    output = [
        [('estética', 0.519), ('cerveja', 0.622), ('engraçado', 0.732), ('pagode', 0.765), ('futebol', 0.855)],
        [('academia', 0.541), ('maquiagem', 0.658), ('estética', 0.765), ('luta', 0.884), ('jiujitsu', 0.921)], 
        [('servers', 0.54), ('culinária', 0.658), ('games', 0.745), ('hardware', 0.865), ('tecnologia', 0.999)],
        [('laboratório', 0.354), ('pesquisa', 0.428), ('comportamento', 0.844), ('skinner', 0.854), ('neurociências', 0.865)]        
    ]

    assert output == questao_2(input)

# Questão 3
def questao_3(posts):
    for post in posts:
        redis_conn.hset(f"post:{post['id']}", mapping=post)

    key_post = redis_conn.keys("post:*")

    for key in key_post:
        redis_conn.expire(key, 3600*5) # Expira em 5 horas (3600 segundos * 5) para cada post

    return [redis_conn.hgetall(key) for key in key_post] # Expira em 5 horas (3600 segundos * 5) para cada post

def test_questao_3():

    input = [
        {"id": '345', "autor":"news_fc@g.com", "data_hora": "2024-06-10 19:51:03", "conteudo": "Se liga nessa lista de jogadores que vão mudar de time no próximo mês!", "palavras_chave": "brasileirao, futebol, cartola, esporte" },
        {"id": '348', "autor":"gastro_pub@g.com", "data_hora": "2024-06-10 19:55:13", "conteudo": "Aprenda uma receita rápida de onion rings super crocantes.", "palavras_chave": "onion rings, receita, gastronomia, cerveja, culinária" },
        {"id": '349', "autor":"make_with_tina@g.com", "data_hora": "2024-06-10 19:56:44", "conteudo": "A dica de hoje envolve os novos delineadores da linha Rare Beauty", "palavras_chave": "maquiagem, estética, beleza, delineador" },
        {"id": '350', "autor":"samarantes@g.com", "data_hora": "2024-06-10 19:56:48", "conteudo": "Eu quando acho a chuteira que perdi na última pelada...", "palavras_chave": "pelada, futebol, cerveja, parceiros" },
        {"id": '351', "autor":"portal9@g.com", "data_hora": "2024-06-10 19:57:02", "conteudo": "No último mês pesquisadores testaram três novos medicamentos para ajudar aumentar o foco.", "palavras_chave": "neurociências, tecnologia, foco, medicamento" },
        {"id": '352', "autor":"meme_e_cia@g.com", "data_hora": "2024-06-10 19:58:33", "conteudo": "Você prefere compartilhar a nossa página agora ou daqui cinco minutos?", "palavras_chave": "entretenimento, engraçado, viral, meme" },
        {"id": '353', "autor":"rnd_hub@g.com", "data_hora": "2024-06-10 19:59:59", "conteudo": "A polêmica pesquisa de V. Damasco sobre ciência do comportamente acaba de ser publicada.", "palavras_chave": "comportamento, ciência, pesquisa, damasco" }
    ]

    assert input == sorted(questao_3(input), key=lambda d: d['id'])

# Questão 4
def questao_4(user_id):
    interests = redis_conn.zrange(f"usuario:{user_id}:interesses", 0, -1, withscores=True)
    keys = redis_conn.keys("post:*")
    posts_peso = []
    for key in keys:
        post = redis_conn.hgetall(key)
        post_interests = post['palavras_chave'].split(", ")
        peso = sum(score for interest, score in interests if interest in post_interests)
        posts_peso.append((post["id"], post['conteudo'], peso))
    
    posts_peso.sort(key=lambda x: x[0])
    posts_peso.sort(key=lambda x: x[2], reverse=True)

    return [content for _, content, _ in posts_peso]

def test_questao_4():

    input = 3 # user_id

    output = [
        "No último mês pesquisadores testaram três novos medicamentos para ajudar aumentar o foco.",
        "Aprenda uma receita rápida de onion rings super crocantes.",
        "Se liga nessa lista de jogadores que vão mudar de time no próximo mês!",
        "A dica de hoje envolve os novos delineadores da linha Rare Beauty",
        "Eu quando acho a chuteira que perdi na última pelada...",
        "Você prefere compartilhar a nossa página agora ou daqui cinco minutos?",
        "A polêmica pesquisa de V. Damasco sobre ciência do comportamente acaba de ser publicada."               
    ]

    assert output == questao_4(input)

# Questão 5
def questao_5(user_views, user_id):
    for user in user_views:
        for view in user['visualizado']:
            redis_conn.lpush(f"usuario:{user['usuario']}:visualizacoes", view)

    vistos = redis_conn.lrange(f"usuario:{user_id}:visualizacoes", 0, -1)
    vistos = [int(view) for view in vistos]

    interests = redis_conn.zrange(f"usuario:{user_id}:interesses", 0, -1, withscores=True)
    keys = redis_conn.keys("post:*")
    posts_peso = []
    for key in keys:
        post = redis_conn.hgetall(key)
        if int(post['id']) in vistos:
            continue
        post_interests = post['palavras_chave'].split(", ")
        peso = sum(score for interest, score in interests if interest in post_interests)
        posts_peso.append((post['id'], post['conteudo'], peso))

    posts_peso.sort(key=lambda item: item[0])
    posts_peso.sort(key=lambda item: item[2], reverse=True)

    conteudos = []
    for post_id, conteudo, peso in posts_peso:
        conteudos.append(conteudo)

    return conteudos

def test_questao_5():

    input = [
        {"usuario":1, "visualizado": [345,350,353]},
        {"usuario":2, "visualizado": [350,351]},
        {"usuario":3, "visualizado": [345,351,352,353]},
        {"usuario":4, "visualizado": []}
    ]

    output = [
        "Aprenda uma receita rápida de onion rings super crocantes.",
        "A dica de hoje envolve os novos delineadores da linha Rare Beauty",
        "Eu quando acho a chuteira que perdi na última pelada..."   
    ]

    assert output == questao_5(input, user_id=3 )


redis_conn.close()