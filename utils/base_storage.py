

class BaseKVStorage[K, V]:
    def __init__(self) -> None:
        self._db: dict[K, V] = {}

    def get_items(self) -> dict[K, V]:
        return self._db

    def set(self, key: K, value: V) -> None:
        self._db[key] = value

    def get(self, key: K) -> V | None:
        return self._db.get(key)

    def unset(self, key: K) -> None:
        self._db[key] = None
