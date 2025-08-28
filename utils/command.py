import sys
from abc import ABC, abstractmethod
from enum import Enum

from utils.base_storage import BaseKVStorage
from utils.db import DBManager


class BaseCommandType(Enum):
    SET = "SET"
    GET = "GET"
    UNSET = "UNSET"
    COUNTS = "COUNTS"
    FIND = "FIND"
    END = "END"
    BEGIN = "BEGIN"
    ROLLBACK = "ROLLBACK"
    COMMIT = "COMMIT"


class BaseCommand[K, V](ABC):
    type: BaseCommandType = None

    def __init__(self, db_manager: DBManager, key: K = None, val: V = None):
        self._db_manager = db_manager
        self.key = key
        self.val = val

        if (
            not hasattr(self, "type")
            or self.type is None
            or self.type not in BaseCommandType
        ):
            err_msg = (f"Attribute 'type' is required for class {self.__class__.__name__}"
                       f"and must be in BaseCommandType.")
            raise AttributeError(err_msg)

    @abstractmethod
    def execute(self):
        raise NotImplementedError()


class SetCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.SET

    def execute(self) -> None:
        if self._db_manager.tr_handler.transaction_exist():
            transaction = self._db_manager.tr_handler.get_last_transaction()
            transaction.items.set(self.key, self.val)
        else:
            self._db_manager.db.set(self.key, self.val)


class GetCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.GET

    def execute(self) -> V | None:
        transactions = self._db_manager.tr_handler.get_transactions()
        if transactions:
            for i in range(len(transactions) - 1, -1, -1):
                if self.key in transactions[i].items.get_items():
                    return transactions[i].items.get(self.key)
        return self._db_manager.db.get(self.key)


class UnsetCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.UNSET

    def execute(self) -> None:
        if self._db_manager.tr_handler.transaction_exist():
            transaction = self._db_manager.tr_handler.get_last_transaction()
            transaction.items.unset(self.key)
        else:
            self._db_manager.db.unset(self.key)


class CountsCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.COUNTS

    def execute(self) -> int:
        total = 0
        items = self._db_manager.db.get_items_for_value(self.val)
        transactions = self._db_manager.tr_handler.get_transactions()

        for transaction in transactions:
            data = transaction.items.get_items()
            items.update(data)

        for v in items.values():
            if v == self.val:
                total += 1
        return total


class FindCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.FIND

    def execute(self) -> list[K]:
        result = []
        items = self._db_manager.db.get_items_for_value(self.val)
        transactions = self._db_manager.tr_handler.get_transactions()

        for transaction in transactions:
            data = transaction.items.get_items()
            items.update(data)

        for k, v in items.items():
            if v == self.val:
                result.append(k)
        return result


class EndCommand[K, V](BaseCommand):
    type: BaseCommandType = BaseCommandType.END

    def execute(self) -> list[K]:
        sys.exit("EndCommand")


class BeginCommand(BaseCommand):
    type: BaseCommandType = BaseCommandType.BEGIN

    def execute(self) -> None:
        self._db_manager.tr_handler.begin()


class RollbackCommand(BaseCommand):
    type: BaseCommandType = BaseCommandType.ROLLBACK

    def execute(self) -> None:
        self._db_manager.tr_handler.rollback()


class CommitCommand(BaseCommand):
    type: BaseCommandType = BaseCommandType.COMMIT

    def _update_context(self, context: BaseKVStorage, data: dict) -> None:
        for k, v in data.items():
            if v is not None:
                context.set(k, v)
            else:
                context.unset(k)

    def execute(self) -> None:
        self._db_manager.tr_handler.check_transactions()
        prev_transaction = self._db_manager.tr_handler.pop_last_transaction()
        data = prev_transaction.items.get_items()

        if self._db_manager.tr_handler.transaction_exist():
            cur_transaction = self._db_manager.tr_handler.get_last_transaction()
            self._update_context(cur_transaction.items, data)
        else:
            self._update_context(self._db_manager.db, data)


class Dispatcher:
    commands: dict[str, type[BaseCommand]] = {
        "SET": SetCommand,
        "GET": GetCommand,
        "UNSET": UnsetCommand,
        "COUNTS": CountsCommand,
        "FIND": FindCommand,
        "BEGIN": BeginCommand,
        "ROLLBACK": RollbackCommand,
        "COMMIT": CommitCommand,
        "END": EndCommand,
    }

    def __init__(self, db_manager: DBManager) -> None:
        self._db_manager = db_manager

    def get_command(self, cmd: str, arg_1: str, arg_2: str) -> BaseCommand:
        if cmd in (
            BaseCommandType.SET.value,
            BaseCommandType.FIND.value,
            BaseCommandType.COUNTS.value
        ):
            if arg_2 is None:
                raise ValueError("Value can't be None")

        command = self.commands.get(cmd)
        if command is None:
            raise ValueError(f"Incorrect command")

        return command(self._db_manager, arg_1, arg_2)
