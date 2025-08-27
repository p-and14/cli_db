from utils.base_storage import BaseKVStorage


class TransactionItems(BaseKVStorage):
    pass


class Transaction:
    def __init__(self) -> None:
        self.items: TransactionItems = TransactionItems()


class TransactionHandler:
    def __init__(self) -> None:
        self._transactions: list[Transaction] = []

    def begin(self) -> None:
        self._transactions.append(Transaction())

    def rollback(self) -> None:
        self._transactions.pop()

    def get_transactions(self) -> list[Transaction]:
        return self._transactions

    def check_transactions(self) -> None:
        if not self._transactions:
            raise RuntimeError("You must first begin the transaction")

    def transaction_exist(self) -> bool:
        return bool(self._transactions)

    def get_last_transaction(self) -> Transaction | None:
        if self.transaction_exist():
            return self._transactions[-1]

    def pop_last_transaction(self) -> Transaction | None:
        if self.transaction_exist():
            return self._transactions.pop()
