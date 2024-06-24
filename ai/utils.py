"""
AI functionality to play in Minecraft
"""

from datetime import datetime, timezone
import pathlib
import requests
import os
import json

from utils.dotenvLoader import loadDotEnv
loadDotEnv()


def getIAMToken(oauthToken: str = str(os.environ.get("YAGPT_OAUTH_TOKEN")), cacheFilename: str = ".iamcache.json") -> dict[str, str]:
    """Вернуть JSON структуру с полями `iamToken` и `expiresAt`. Кэшируется в файл  `.iamcache.json`

    Args:
        oauthToken (str, optional): Токен авторизации, полученный по ссылке в [документации](https://yandex.cloud/ru/docs/iam/operations/iam-token/create). Defaults to str(os.environ.get("YAGPT_OAUTH_TOKEN")).
        cacheFilename (str, optional): Имя файла для кеширования токена. Defaults to ".iamcache.json".

    Returns:
        dict[str, str]: _description_
    """
    def req() -> dict[str, str]:
        r = requests.post("https://iam.api.cloud.yandex.net/iam/v1/tokens", json={
            "yandexPassportOauthToken": oauthToken
        })
        return r.json()
    
    def cache(response: dict[str, str]):
        with open(pathlib.Path(cwd, cacheFilename).absolute(), "w") as file:
            json.dump(response, file)
    
    cwd = pathlib.Path().cwd().absolute()
    
    if cacheFilename in os.listdir(cwd):
        with open(pathlib.Path(cwd, cacheFilename).absolute(), "r") as file:
            r = json.load(file)
            
        if datetime.fromisoformat(r["expiresAt"].rstrip('Z')).replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            response = req()
            cache(response)
            return response
        else:
            return r
    else:
        r = req()
        cache(r)
        return r
    

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

def createMessageBody(text: str, role: str = "user") -> dict[str, str]:
    return {
        "role": role,
        "text": text
    }



class ROLES(object):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

