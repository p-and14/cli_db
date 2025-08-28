from utils.base_storage import BaseKVStorage
from utils.transaction import TransactionHandler


class DB[K, V](BaseKVStorage):
    def get_items_for_value(self, value: V) -> dict[K, V]:
        return {k: v for k, v in self._db.items() if v == value}


class DBManager:
    def __init__(self, database: DB, tr_handler: TransactionHandler) -> None:
        self.db = database
        self.tr_handler = tr_handler
