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
    def __init__(self, 
                folder_id: str, 
                iam_token: str, 
                model: str = "yandexgpt",
                data_logging_enabled: bool = True,
                
                stream: bool = False, 
                temperature: float = 0.1, 
                maxTokens: int = 1000,
                
                generation_segment: str | None = None,
                
                systemPrompt: str = f"Ты - эксперт по игре Minecraft. Тебя зовут {os.environ.get("BOT_USERNAME")}. Свой пол определи в зависимости от твоего имени. Все свои сообщения ты пишешь в чат внутри игры Minecraft. Не используй разметку Markdown! Отвечай, словно ты настоящий человек и игрок в Minecraft."):
        """Инициализирует возможность общаться с нейронной сетью YaGPT. Подробнее читайте [здесь](https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/create-prompt)

        Args:
            folder_id (str): идентификатор каталога, на который у вашего аккаунта есть роль ai.languageModels.user или выше.
            iam_token (str): IAM-токен, полученный перед началом работы.
            model (str, optional): Наименование языковой модели. Defaults to "yandexgpt".
            data_logging_enabled (bool, optional): Определяет, будут ли сообщения логироваться на строне Яндекса. Defaults to True.
            stream (bool, optional): включает потоковую передачу частично сгенерированного текста. Принимает значения true или false. Defaults to False.
            temperature (float, optional): чем выше значение этого параметра, тем более креативными и случайными будут ответы модели. Принимает значения от 0 (включительно) до 1 (включительно). Defaults to 0.1.
            maxTokens (int, optional): устанавливает ограничение на выход модели в токенах. Максимальное число токенов генерации зависит от модели. Подробнее см. в разделе Квоты и лимиты в Yandex Foundation Models. Defaults to 1000.
            generation_segment (str | None, optional): Сегменты `/latest`, `/rc` и `/deprecated` указывают версию модели. Defaults to None.
            systemPrompt (str, optional): позволяет задать контекст запроса и определить поведение модели. Defaults to f"Ты - эксперт по игре Minecraft. Тебя зовут {os.environ.get("BOT_USERNAME")}. Все свои сообщения ты пишешь в чат внутри игры Minecraft. Не используй разметку Markdown! Отвечай, словно ты настоящий человек и игрок в Minecraft.".
        """
        
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.model_uri = f"gpt://{folder_id}/{model}/{generation_segment}" if generation_segment else f"gpt://{folder_id}/{model}"
        
        self.folder_id: str = folder_id
        self.iam_token: str = iam_token
        self.data_logging_enabled: bool = data_logging_enabled
        self.stream: bool = stream
        self.temperature: float = temperature
        self.maxTokens: int = maxTokens
        self.generation_segment: str | None = generation_segment
        
        self.systemPrompt = systemPrompt
        self.messages = [self._createMessageBody(systemPrompt, "system")]
        self.completion = None
    
    def _appendMessage(self, text: str, role: str = "user") -> list[dict]:
        """Сохраняет сообщение в историю чата

        Args:
            text (str): Текст сообщения
            role (str, optional): Роль автора сообщения: `user`, `system` или `assistant`. Defaults to "user".

        Returns:
            list[dict]: Список словарей, содержащих текст сообщения и роль автора сообщения
        """
        self.messages.append(self._createMessageBody(text, role))
        return self.messages
        
    def _createRequestBody(self) -> dict:
        return {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": self.stream,
                "temperature": self.temperature,
                "maxTokens": f"{self.maxTokens}"
            },
            "messages": self.messages
        }
    
    def _createMessageBody(self, text: str, role: str = "user") -> dict:
        return {
            "role": role,
            "text": text
        }
    
    def ask(self, messageText: str, typeUser: str = "user") -> str:
        message_body = self._createMessageBody(messageText, typeUser)
        self.messages.append(message_body)
        
        request_body = self._createRequestBody()
        r = requests.post(self.api_url, json=request_body, headers={
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": f"{self.folder_id}",
            "x-data-logging-enabled": f"{self.data_logging_enabled}".lower()
        })
        
        if r.status_code:
            print("\n\n\nREQUEST:", json.dumps(request_body, indent=4))
            print("RESPONSE:", json.dumps(r.json(), indent=2))
            response_message = r.json()["result"]["alternatives"][0]["message"]["text"]
            self._appendMessage(response_message, "assistant")
            return response_message
        else:
            return "!Ошибка в языковой модели"


