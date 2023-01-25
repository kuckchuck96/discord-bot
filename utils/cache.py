from expiringdict import ExpiringDict


class Cache():
    ''' Set or get key value pair with expiry '''
    def __init__(self, size, expiry):
        self.cache = ExpiringDict(max_len=size, max_age_seconds=expiry)

    def set(self, key, value):
        self.cache[key] = value
        
    def get(self, key):
        return self.cache.get(key)


