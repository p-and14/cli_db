import sys

from utils.command import Dispatcher
from utils.db import DB, DBManager
from utils.parser import CLIParser, Formatter
from utils.transaction import TransactionHandler


cli_parser = CLIParser()
db = DB()
transaction_handler = TransactionHandler()
db_manager = DBManager(db, transaction_handler)
dispatcher = Dispatcher(db_manager)


def main()  -> None:
    while True:
        user_input = sys.stdin.readline().strip()
        try:
            cmd_info = cli_parser.parse(user_input)
            cmd = dispatcher.get_command(*cmd_info)
            res = cmd.execute()
            Formatter.display_result(cmd.type, res)
        except (ValueError, RuntimeError) as e:
            Formatter.display_error(e)


if __name__ == "__main__":
    main()
