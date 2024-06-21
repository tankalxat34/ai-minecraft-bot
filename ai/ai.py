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

def createRequestBody(model_uri: str, stream: bool, temperature: float, maxTokens: int, messages: list) -> dict:
    """Создает тело для POST запроса к нейронной сети

    Returns:
        dict: Словарь, являющийся JSON телом запроса
    """
    return {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": stream,
            "temperature": temperature,
            "maxTokens": f"{maxTokens}"
        },
        "messages": messages
    }



class AiSession:
    def __init__(self, 
                # авторизация
                folder_id: str, 
                iam_token: str, 
                # имя бота в игре
                name: str,
                model: str = "yandexgpt",
                data_logging_enabled: bool = False,
                
                stream: bool = False, 
                temperature: float = 0.1, 
                maxTokens: int = 1000,
                
                generation_segment: str | None = None,
                
                systemPrompt: str = "Ты - эксперт по игре Minecraft. Тебя зовут {name}. Ты находишься внутри игры Minecraft. Свой пол определи в зависимости от твоего имени. Все свои сообщения ты пишешь в чат внутри игры Minecraft игроку. Не используй разметку Markdown! Отвечай, словно ты настоящий человек. Ты дружелюбен и приветлив."):
        """Инициализирует возможность общаться с нейронной сетью YaGPT. Подробнее читайте [здесь](https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/create-prompt)

        Args:
            folder_id (str): идентификатор каталога, на который у вашего аккаунта есть роль ai.languageModels.user или выше.
            iam_token (str): IAM-токен, полученный перед началом работы.
            name (str): Имя бота в игре.
            model (str, optional): Наименование языковой модели. Defaults to "yandexgpt".
            data_logging_enabled (bool, optional): Определяет, будут ли сообщения логироваться на строне Яндекса. Defaults to True.
            stream (bool, optional): включает потоковую передачу частично сгенерированного текста. Принимает значения true или false. Defaults to False.
            temperature (float, optional): чем выше значение этого параметра, тем более креативными и случайными будут ответы модели. Принимает значения от 0 (включительно) до 1 (включительно). Defaults to 0.1.
            maxTokens (int, optional): устанавливает ограничение на выход модели в токенах. Максимальное число токенов генерации зависит от модели. Подробнее см. в разделе Квоты и лимиты в Yandex Foundation Models. Defaults to 1000.
            generation_segment (str | None, optional): Сегменты `/latest`, `/rc` и `/deprecated` указывают версию модели. Defaults to None.
            systemPrompt (str, optional): позволяет задать контекст запроса и определить поведение модели.
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
        self.name: str = name
        
        self.systemPrompt = systemPrompt.format(name=self.name)
        self.messages = [self._createMessageBody(self.systemPrompt, "system")]
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
        
    def _createRequestBody(self, useChatHistory: bool = True) -> dict:
        """Создать тело для POST запроса на сервер

        Args:
            useChatHistory (bool, optional): Использовать ли историю чата для сохранения контекста беседы. Defaults to True.

        Returns:
            dict: Словарь-тело для запроса
        """
        return createRequestBody(
            model_uri=self.model_uri,
            maxTokens=self.maxTokens,
            messages=self.messages if useChatHistory else [self._createMessageBody(self.systemPrompt, "system")],
            stream=self.stream,
            temperature=self.temperature,
        )
    
    def _createMessageBody(self, text: str, role: str = "user") -> dict:
        return {
            "role": role,
            "text": text
        }
    
    def _createSystemMessageBody(self) -> dict:
        """Создает системное сообщение. Такое сообщение должно быть начальным в истории чата и задавать контекст для дальнейшей
        беседы

        Returns:
            dict: Словарь-тело для системного сообщения
        """
        return self._createMessageBody(self.systemPrompt, "system")
        
    def clearChatHistory(self):
        """Очищает историю сообщений
        """
        self.messages.clear()
        self._appendMessage(*self._createSystemMessageBody())
    
    def ask(self, messageText: str, typeUser: str = "user", useChatHistory: bool = True) -> str:
        """Выполнить запрос к нейросети YaGPT

        Args:
            messageText (str): Текст сообщения для выполнения запроса
            typeUser (str, optional): Тип пользователя. Defaults to "user".
            useChatHistory (bool, optional): Сделать запрос с учетом истории предыдущих сообщений. Если `False` - отправленное сообщение будет считаться первым в диалоге. Defaults to True.

        Returns:
            str: Строка с ответом нейронной сети
        """
        self._appendMessage(messageText, typeUser)
        request_body: dict = self._createRequestBody(useChatHistory)

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


