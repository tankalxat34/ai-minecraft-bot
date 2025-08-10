from dotenv import load_dotenv
import os
# Загрузить переменные из файла .env
load_dotenv()

import sys
from openai import OpenAI

import utils.structures as s
from utils.model_settings import MODEL_SETTINGS

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key=os.environ["API_TOKEN"],
)

with open(".\\prompts\\minecraft.md") as prompt:
    chat = s.Chat(prompt.read())

print(chat)

last_message = ""
while last_message != "!exit":
    last_message = input(f"{s.Role.USER}>>> ")
    chat.push(s.Role.USER, last_message)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=chat.chat,
        **MODEL_SETTINGS
    )

    chat.push(completion.choices[::-1][0].message.role, completion.choices[::-1][0].message.content)
    print(f"{chat.last()['role']}>>>", chat.last()["content"])
