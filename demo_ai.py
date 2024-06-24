"""Это демо-режим общения с YandexGPT через консоль
"""

import json
from typing import Any, Callable
import os

import ai.prompts
import ai.utils
import ai.session
from utils.botUtils import CommandsComparator
from utils.dotenvLoader import loadDotEnv
import difflib


loadDotEnv()
print(__doc__)

def action_prototype(f: Callable):
    def wrapper():
        print("Выполняю функцию", f.__name__, end=" ")
        res = f()
        print("выполнил")
        return res
    return wrapper
        
    
@action_prototype
def action_followMe():
    pass

@action_prototype
def action_stop():
    pass

# инициализация действий бота
BOT_ACTIONS = {
    "стоп": lambda: action_stop(),
    "за мной": lambda: action_followMe(),
}

# инициализация беседы с YandexGPT
yagpt = ai.session.YaGPTSession(
    folder_id=os.environ.get("YAGPT_FOLDERID"), # type: ignore
    iam_token=ai.utils.getIAMToken()["iamToken"],
    temperature=0.1,
    maxTokens=1000,
    formatMapForSystemPrompt={
        "name": "Alice",
        "commands": ", ".join(list(BOT_ACTIONS.keys()))
    }
)

# команды для выполнения методов YaGPTSession (кроме `.ask()`)
DEFAULT_COMMAND_PREFIX = "!"
DEFAULT_COMMANDS: dict[str, Callable[[], tuple[Any, str]]] = { # type: ignore
    "clear": lambda: (yagpt.clearChatHistory(), "История очищена")
}

# создание компаратора бота с возможными командами
comparator = CommandsComparator(BOT_ACTIONS, aiSession=yagpt)



while True:
    prompt = input(">>> ")
    
    if (prompt[0] == DEFAULT_COMMAND_PREFIX) and (prompt[1:] in DEFAULT_COMMANDS.keys()):
        print(DEFAULT_COMMANDS[prompt[1:]]()[1])
    else:
        result = comparator.compare(prompt)()
        if type(result).__name__ == "str":
            print(result)
