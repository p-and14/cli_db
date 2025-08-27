import re
from typing import Any

from utils.command import BaseCommandType


class CLIParser:
    pattern = re.compile(
        r'(?i)^\s*'
        rf'(?P<cmd>{"|".join([com.value for com in BaseCommandType])})'
        r'(?:\s+(?P<key>\S+))?'
        r'(?:\s+(?P<value>\S+))?'
        r'\s*$'
    )

    def parse(self, user_input: str) -> tuple[str, str, str]:
        match = self.pattern.match(user_input)
        if not match:
            raise RuntimeError("Incorrect command")

        cmd, arg_1, arg_2 = match.groups()
        cmd = cmd.upper()

        if cmd in (BaseCommandType.FIND.value, BaseCommandType.COUNTS.value):
            return cmd, arg_2, arg_1

        return cmd, arg_1, arg_2

class Formatter:
    @staticmethod
    def display_result(
        cmd_type: BaseCommandType,
        result: Any
    ) -> None:
        if cmd_type in (
            BaseCommandType.GET,
            BaseCommandType.COUNTS,
            BaseCommandType.FIND
        ):
            print(result)

    @staticmethod
    def display_error(
        error: Exception,
    ) -> None:
        print(error)
