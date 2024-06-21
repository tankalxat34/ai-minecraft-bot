"""
This is a part of Python Package Manager

https://github.com/tankalxat34/ppm

(c) tankalxat34
"""

import re
from typing import Any


class Prefix(object):
    INFO = "INFO"
    WARGING = "WARN"
    ERROR = "ERROR"


class Options(object):
    YESNO = ["y", "n"]
    NOYES = ["n", "y"]


class Cli:
    def __init__(self, commandString: str):
        cmdParts = tuple(map(lambda x: x.strip(), commandString.split(" ")))
        _strOptions = re.findall(r"\-\-\S+=?", commandString)  # \-\-\w+=?(\".+\")*

        self.command: str = cmdParts[0]
        self.arguments: list[str] = []
        self.options: dict[str, str | bool] = {}
        self.aliases: list[str] = list(
            map(lambda x: x[2:], re.findall(r" \-\w{1}", commandString))
        )
        self.cmd: str = commandString

        for opt in _strOptions:
            if "=" in opt:
                k, v = opt.split("=")
                self.options[k[2:]] = v
            else:
                self.options[opt[2:]] = True

        for arg in cmdParts:
            if (arg[0] != "-") and (arg != self.command) and (arg not in _strOptions):
                self.arguments.append(arg)

    def getOption(self, name: str) -> Any:
        try:
            return self.options[name]
        except KeyError:
            return None

    @staticmethod
    def stdout(
        *args,
        level: int = 0,
        intendSize: int = 2,
        prefix: str = "",
    ) -> None:
        print(" " * intendSize * level, f"[{prefix}] " if prefix else "", *args, sep="")

    @staticmethod
    def stdin(
        message: str,
        options: list[str] = [],
        defaultOption: str | int = 0,
        errorIfUnknownOption: bool = False,
        useDefault: bool = False,
    ):
        """Custom input wrapper"""
        if type(defaultOption) == int:
            defaultOption = options[defaultOption]

        if useDefault:
            return defaultOption

        response = (
            input(
                f"{message} ({', '.join((map(lambda x: x.upper() if x == defaultOption else x, options)))})"
                + ": "
            )
            or defaultOption
        )

        if len(options) and (response not in options) and errorIfUnknownOption:
            raise ValueError(f"Unknown option '{response}'")

        return response

    def __str__(self) -> str:
        return self.cmd


if __name__ == "__main__":
    # command = Cli('git commit -h --message="commit message" --file=text.txt')
    # Cli.stdout("Hello world")
    # Cli.stdout("Second", level=1)
    # Cli.stdout("Third line", level=2)
    # Cli.stdout("Fourth line", level=1)
    print()
