from cachetools import TTLCache


class InstanceDatabase:
    def __init__(self, maxsize: int = 3000, ttl: int = 240):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str):
        try:
            item = self.cache[key]

            return item
        except KeyError:
            return None

    def set(self, key: str, value):
        self.cache[key] = value
        return value
