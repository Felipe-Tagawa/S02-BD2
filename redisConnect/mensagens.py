import redis

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)


class CacheBase(RedisClient):
    def set(self, key: str, mapping: dict) -> bool:
        return self.client.hset(key, mapping=mapping)

    def get(self, key: str) -> dict:
        return self.client.hgetall(key)

    def set_ttl(self, key: str, seconds: int) -> bool:
        return self.client.expire(key, seconds)

    def get_ttl(self, key: str) -> int:
        return self.client.ttl(key)
    
class UsuarioCache(CacheBase):
    pass
    
class MensagemCache(CacheBase):
    pass

import threading

class Publisher(RedisClient):
    def publish(self, channel: str, message: str) -> int:
        return self.client.publish(channel, message)

class Subscriber(RedisClient):
    def subscribe(self, channel: str):
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message["type"] == "message":
                print(f"[{channel}] {message['data']}")

if __name__ == "__main__":
    import time
    u = UsuarioCache()
    m = MensagemCache()

    u.set("usuario:1", {"id": "1", "nome": "Kyo", "email": "kyo@gmail.com"})
    u.set_ttl("usuario:1", 60)

    u.set("usuario:2",{"id": "2", "nome": "Alice", "email": "alice@email.com"})
    u.set_ttl("usuario:2", 60)

    m.set("mensagem:1", {"id": "1", "hora": "10:00:00", "data": "2025-12-12", "conteudo": "bao?", "remetente": "usuario:1", "destinatario": "usuario:2"})
    m.set_ttl("mensagem:1", 5)

    m.set("mensagem:2", {"id": "2", "hora": "10:02:00", "data": "2025-12-12", "conteudo": "top?", "remetente": "usuario:2", "destinatario": "usuario:1"})
    m.set_ttl("mensagem:2", 5)

    # Exibicao:
    print("Usuários")
    print(u.get("usuario:1"))
    print(u.get("usuario:2"))

    print("\nMensagens")
    print(m.get("mensagem:1"))
    print(m.get("mensagem:2"))

    print("Aguardando um tempo...")
    time.sleep(6)

    print("\nMensagens após expiração")
    print(m.get("mensagem:1"))  # {}
    print(m.get("mensagem:2"))  # {}

    print("\nUsuários ainda ativos")
    print(u.get("usuario:1"))
    print(u.get("usuario:2"))

    sub = Subscriber()
    pub = Publisher()

    thread = threading.Thread(target=sub.subscribe, args=("canal:geral",))
    thread.daemon = True
    thread.start()

    import time
    time.sleep(1)

    pub.publish("canal:geral", "oi pessoal")
    pub.publish("canal:geral", "alguem ai?")

    time.sleep(1)