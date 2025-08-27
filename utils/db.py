from utils.base_storage import BaseKVStorage
from utils.transaction import TransactionHandler


class DB(BaseKVStorage):
    pass


class DBManager:
    def __init__(self, database: DB, tr_handler: TransactionHandler) -> None:
        self.db = database
        self.tr_handler = tr_handler
