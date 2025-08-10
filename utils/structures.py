"""
Модуль для работы с основными структурами данных
"""

import datetime
import json

def getTimestamp() -> int:
    return int(datetime.datetime.now().timestamp())

def makeMessage(role: str, content: str) -> dict:
    """
    Возвращает объект с сообщением
    """
    return {
        "timestamp": str(getTimestamp()),
        "role": role,
        "content": content
    }

def getSystemPrompt(path: str = ".\\prompts\\system_prompt.md") -> str:
    """
    Вернуть системный промпт
    """
    with open(path, "r") as f:
        return f.read()

class Role(object):
    """
    Роль в чате
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Chat:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.chat: list[dict] = [makeMessage("system", self.system_prompt)]

    def __str__(self):
        return json.dumps(self.chat, indent=2)

    def push(self, role: Role, content: str):
        """
        Добавить сообщение в чат

        Needs add overload to wrk with completitions
        """
        self.chat.append(makeMessage(role, content))
    
    def last(self) -> dict:
        """
        Вернуть последнее сообщение
        """
        return self.chat[::-1][0]