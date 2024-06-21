"""
AI functionality to play in Minecraft
"""

import requests
import os
import json

from helper import loadDotEnv
loadDotEnv()


def getIAMToken(oauthToken: str = str(os.environ.get("YAGPT_OAUTH_TOKEN"))) -> dict[str, str]:
    r = requests.post("https://iam.api.cloud.yandex.net/iam/v1/tokens", json={
        "yandexPassportOauthToken": oauthToken
    })
    return r.json()



class AiSession:
    def __init__(self, folder_id: str, iam_token: str, model: str = "yandexgpt-lite", systemPrompt: str = "Ты - эксперт по игре Minecraft"):
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.model_uri = f"gpt://{folder_id}/{model}"
        
        self.folder_id = folder_id
        self.iam_token = iam_token
        
        self.systemPrompt = systemPrompt
        self.messages = [self._createMessageBody(systemPrompt, "system")]
        self.completion = None
    
    def _createRequestBody(self, stream: bool = False, temperature: float = 0.1, maxTokens: int = 1000) -> dict:
        return {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": f"{maxTokens}"
            },
            "messages": self.messages
        }
    
    def _createMessageBody(self, text: str, role: str = "user") -> dict:
        return {
            "role": role,
            "text": text
        }
    
    def ask(self, messageText: str, typeUser: str = "user", *args, **kwargs) -> str:
        self.messages.append(self._createMessageBody(messageText, typeUser))
        
        r = requests.post(self.api_url, json=self._createRequestBody(**kwargs), headers={
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": f"{self.folder_id}"
        })
        
        if r.status_code:
            return r.json()["result"]["alternatives"][0]["message"]["text"]
        else:
            return "!Ошибка в языковой модели"


