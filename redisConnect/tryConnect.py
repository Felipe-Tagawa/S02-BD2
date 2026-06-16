import redis
import time

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def ping(self) -> bool:
        return self.client.ping()
    
    def set_ttl(self, key: str, seconds: int) -> bool:
        return self.client.expire(key, seconds)
    
    def get_ttl(self, key: str) -> int:
        return self.client.ttl(key)
    
class StringStore(RedisClient): # Treino de String
    def set(self, key: str, value: str) -> bool:
        return self.client.set(key, value)
    
    def get(self, key: str) -> str | None:
        return self.client.get(key)
    
    def delete(self, key: str) -> int:
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key)
    
    def increment(self, key: str) -> int:
        return self.client.incr(key)
    
class HashStore(RedisClient):
    def set(self, key: str, mapping: dict) -> bool:
        return self.client.hset(key, mapping=mapping)
    def get(self, key: str) -> dict:
        return self.client.hgetall(key)
    def get_field(self, key: str, field: str) -> str | None:
        return self.client.hget(key, field)
    def delete_field(self, key: str, field: str) -> int:
        return self.client.hdel(key, field)
    
class ListStore(RedisClient):
    def push(self, key: str, *values: str) -> int:
        return self.client.rpush(key, *values)
    
    def pop(self, key: str) -> str | None:
        return self.client.lpop(key)
    
    def get_all(self, key: str) -> list:
        return self.client.lrange(key, 0, -1) # Comeca no 0 vai até -1 (último)
    
    def length(self, key: str) -> int:
        return self.client.llen(key)
    
class SetStore(RedisClient):
    def add(self, key: str, *values: str) -> int:
        return self.client.sadd(key, *values)
    
    def remove(self, key: str, value: str) -> int:
        return self.client.srem(key, value)
    
    def get_all(self, key: str) -> set:
        return self.client.smembers(key)
    
    def is_member(self, key: str, value: str) -> bool:
        return self.client.sismember(key, value)
    
class SortedSetStore(RedisClient):
    def add(self, key: str, mapping: dict) -> int:
        return self.client.zadd(key, mapping)
    
    def get_all(self, key: str) -> list:
        return self.client.zrange(key, 0, -1, withscores=True)
    
    def get_score(self, key: str, member: str) -> float | None:
        return self.client.zscore(key, member)
    
    def remove(self, key: str, member: str) -> int:
        return self.client.zrem(key, member)
    

if __name__ == "__main__":
    """
    s = StringStore()
    s.set("nome", "Felipe")
    print(s.get("nome"))
    s.delete("nome")
    print(s.get("nome"))
    s.set("contador", "0")
    print(s.increment("contador"))
    print(s.increment("contador"))
    print(s.exists("contador"))
    print(s.exists("nao-existe"))
    

    h = HashStore()

    h.set("usuario:1", {"nome": "kyo", "idade": "22", "cidade": "Santa Rita"})
    print(h.get("usuario:1"))
    print(h.get_field("usuario:1", "nome"))
    h.delete_field("usuario:1", "cidade")
    print(h.get("usuario:1"))

    l = ListStore()


    l.client.delete("fila")
    l.push("fila", "tarefa1", "tarefa2", "tarefa3")
    print(l.get_all("fila"))  # ['tarefa1', 'tarefa2', 'tarefa3']
    print(l.pop("fila"))      # tarefa1
    print(l.get_all("fila"))  # ['tarefa2', 'tarefa3']
    print(l.length("fila"))   # 2

    s = SetStore()

    s.add("tags", "python", "redis", "backend", "python")  # python duplicado
    print(s.get_all("tags"))       # sem duplicata
    print(s.is_member("tags", "redis"))   # True
    print(s.is_member("tags", "java"))    # False
    s.remove("tags", "backend")
    print(s.get_all("tags"))
    """

    ss = SortedSetStore()

    ss.add("ranking", {"kyo": 100, "alice": 80, "bob": 95})
    print(ss.get_all("ranking"))     # ordenado pelo score
    print(ss.get_score("ranking", "kyo"))
    ss.remove("ranking", "alice")
    print(ss.get_all("ranking"))

    s = StringStore()
    s.set("sessao", "abc123")
    s.set_ttl("sessao", 5)

    print(s.get_ttl("sessao"))  # ~5
    time.sleep(6)
    print(s.get("sessao"))      # None
    print(s.get_ttl("sessao"))  # -2



