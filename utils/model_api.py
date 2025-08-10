from dotenv import load_dotenv
import os

from utils.model_settings import MODEL_SETTINGS
# Загрузить переменные из файла .env
load_dotenv()

import sys
from openai import OpenAI

def makeMessage(role: str, content: str) -> dict:
    """
    Создает словарь с сообщением
    """
    return {
        "role": role,
        "content": content
    }

class Model:
    def __init__(self, model: str, base_url: str, system_prompt: str, api_token: str = os.environ["API_TOKEN"]):
        self.model = model
        self.base_url = base_url
        self.api_token = api_token
        self.system_prompt = system_prompt

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_token,
        )

        self.chat: list[dict] = [
            makeMessage("system", system_prompt)
        ]

    def ask(self, message: str) -> str:
        self.chat.append(makeMessage("user", message))

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.chat,
            **MODEL_SETTINGS
        )

        role, content = completion.choices[::-1][0].message.role, completion.choices[::-1][0].message.content
        self.chat.append(makeMessage(role, content))
        
        return content

    