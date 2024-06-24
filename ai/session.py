"""Класс для работы с YandexGPT
"""
from typing import Any
from requests import Response
import requests

from ai import prompts
from ai.utils import createMessageBody, createRequestBody



class YaGPTSession:
    """Клиент для общения с нейронной сетью YaGPT. Подробнее читайте [здесь](https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/create-prompt)"""
    def __init__(
                    self,
                    # авторизация
                    folder_id: str,
                    iam_token: str,
                    # имя бота в игре
                    model: str = "yandexgpt",
                    data_logging_enabled: bool = False,

                    stream: bool = False,
                    temperature: float = 0.1,
                    maxTokens: int = 1000,

                    generation_segment: str | None = None,

                    systemPrompt: str = prompts.Prompts.SYSTEM_PROMPT_2,
                    formatMapForSystemPrompt: dict[str, str] = {}
                ):
        """Клиент для общения с нейронной сетью YaGPT. Подробнее читайте [здесь](https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/create-prompt)

        Args:
            folder_id (str): идентификатор каталога, на который у вашего аккаунта есть роль ai.languageModels.user или выше.
            iam_token (str): IAM-токен, полученный перед началом работы.
            model (str, optional): Наименование языковой модели. Defaults to "yandexgpt".
            data_logging_enabled (bool, optional): Определяет, будут ли сообщения логироваться на строне Яндекса. Defaults to False.
            stream (bool, optional): включает потоковую передачу частично сгенерированного текста. Принимает значения true или false. Defaults to False.
            temperature (float, optional): чем выше значение этого параметра, тем более креативными и случайными будут ответы модели. Принимает значения от 0 (включительно) до 1 (включительно). Defaults to 0.1.
            maxTokens (int, optional): устанавливает ограничение на выход модели в токенах. Максимальное число токенов генерации зависит от модели. Подробнее см. в разделе Квоты и лимиты в Yandex Foundation Models. Defaults to 1000.
            generation_segment (str | None, optional): Сегменты `/latest`, `/rc` и `/deprecated` указывают версию модели. Defaults to None.
            systemPrompt (str, optional): позволяет задать контекст запроса и определить поведение модели.
            formatMapForSystemPrompt (dict[str, str], optional): Словарь с дополнительными значениями для форматирования промпта. Позволяет на этапе инициализации сессии создать корректный системный промпт.
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
        
        for k in formatMapForSystemPrompt.keys():
            try:
                self.systemPrompt = self.systemPrompt.format(**{f"{k}": formatMapForSystemPrompt[k]})
            except Exception:
                pass
        
        
        self.messages = [self._createMessageBody(self.systemPrompt, "system")]
        self.completion = None
        
        self.DEFAULT_MESSAGE_HISTORY = [self._createMessageBody(self.systemPrompt, "system")]
        """Возвращает массив с одним `system` сообщением.
        ```
        [
            {
                "role": "system",
                "text:" "Это системный промпт"
            }
        ]
        ```
        """

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
        return createMessageBody(text, role)

    def _createSystemMessageBody(self) -> dict:
        """Создает системное сообщение. Такое сообщение должно быть начальным в истории чата и задавать контекст для дальнейшей
        беседы

        Returns:
            dict: Словарь-тело для системного сообщения
        """
        return self._createMessageBody(self.systemPrompt, "system")

    def _post(self, request_body: dict[str, Any]) -> requests.Response:
        return requests.post(self.api_url, json=request_body, headers={
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json",
            "x-folder-id": f"{self.folder_id}",
            "x-data-logging-enabled": f"{self.data_logging_enabled}".lower()
        })
        
    def _responseValidation(self, r: Response):
        if r.status_code:
            response_message: str = r.json()["result"]["alternatives"][0]["message"]["text"]
            self._appendMessage(response_message, "assistant")
            return response_message
        else:
            return "!Ошибка в языковой модели"

    def clearChatHistory(self):
        """Очищает историю сообщений
        """
        self.messages.clear()
        self.messages.append(self._createSystemMessageBody())

    def ask(self, messageText: str, typeUser: str = "user", useChatHistory: bool = True, **kwargs) -> str:
        """Выполнить запрос к нейросети YaGPT

        Args:
            messageText (str): Текст сообщения для выполнения запроса
            typeUser (str, optional): Тип пользователя. Defaults to "user".
            useChatHistory (bool, optional): Сделать запрос с учетом истории предыдущих сообщений. Если `False` - отправленное сообщение будет считаться первым в диалоге. Defaults to True.
            kwargs (dict[str, Any], optional): Необязательно. Ручное переопределение тела запроса. Можно переопределить такие параметры, как `temperature`, `maxTokens`, `messages` и т.д. для конкретного запроса.

        Returns:
            str: Строка с ответом нейронной сети
        """
        self._appendMessage(messageText, typeUser)
        request_body: dict = self._createRequestBody(useChatHistory)
        
        # переопределение тела запроса
        for kwarg in kwargs.keys():
            request_body[kwarg] = kwargs[kwarg]
            
        print(f"{request_body =}")

        r = self._post(request_body)
        return self._responseValidation(r)
        

    def customAsk(
            self,
            messages: list[dict[str, str]],
            **kwargs
        ) -> str:
        """Выполнить кастомный запрос к нейросети YaGPT

        Args:
            kwargs (dict[str, Any], optional): Необязательно. Ручное переопределение тела запроса. Можно переопределить такие параметры, как `temperature`, `maxTokens`, `messages` и т.д. для конкретного запроса.

        Returns:
            str: Строка с ответом нейронной сети
        """
        request_body: dict = createRequestBody(
            model_uri=kwargs["model_uri"] if "model_uri" in kwargs.keys() else self.model_uri,
            stream=kwargs["stream"] if "stream" in kwargs.keys() else self.stream,
            temperature=kwargs["temperature"] if "temperature" in kwargs.keys() else self.temperature,
            maxTokens=kwargs["maxTokens"] if "maxTokens" in kwargs.keys() else self.maxTokens,
            messages=messages
        )
        
        r = self._post(request_body)
        return self._responseValidation(r)