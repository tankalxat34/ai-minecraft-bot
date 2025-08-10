from dotenv import load_dotenv
import os
# Загрузить переменные из файла .env
load_dotenv()

import sys
from openai import OpenAI
from javascript import require, On

import utils.structures as s
import utils.actions as a
from utils.model_settings import MODEL_SETTINGS

# инициализация
## chatgpt

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key=os.environ["API_TOKEN"],
)

with open(".\\prompts\\minecraft.md") as prompt:
    chat = s.Chat(prompt.read())

## minecraft bot
mineflayer = require("mineflayer")
pathfinder = require("mineflayer-pathfinder")

bot = mineflayer.createBot({
    "host": "127.0.0.1",
    "port": "60536",
    "username": "_jeb",
    "version": "1.21.5"
})

mcData = require("minecraft-data")(bot.version)

bot.loadPlugin(pathfinder.pathfinder)
movements = pathfinder.Movements(bot, mcData)

# completion = client.chat.completions.create(
#     model="openai/gpt-oss-20b",
#     messages=chat.chat,
#     **MODEL_SETTINGS
# )

@On(bot, "spawn")
def spawn(*args):
    a.log("OK")
    bot.chat("Я появился")

@On(bot, "whisper")
def whisper(this, username: str, message: str, *args):
    a.log("OK")
    bot.whisper(username, message)



    # @On(bot, "chat")
    # def chatHandler(this, username: str, message: str, *args):
    #     bot.whisper(username, f"Напиши мне командой `/tell %username% <твое_сообщение>` и тогда я смогу помочь!")

    # @On(bot, "whisper")
    # def whisperHandler(this, username: str, message: str, *args):
    #     chat.push(s.Role.USER, message)

    #     a.log("Получено сообщение", message)

    #     completion = client.chat.completions.create(
    #         model="openai/gpt-oss-20b",
    #         messages=chat.chat,
    #         **MODEL_SETTINGS
    #     )

    #     a.log("Сформирован ответ", completion.choices[::-1][0].message.content)

    #     chat.push(completion.choices[::-1][0].message.role, completion.choices[::-1][0].message.content)
    #     bot.whisper(username, f"{chat.last()["content"]}")
        