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

from utils.model_api import Model

# инициализация
## chatgpt

with open(".\\prompts\\minecraft.md") as prompt:
    system_prompt = prompt.read()

model = Model(
    model="openai/gpt-oss-20b",
    base_url="http://localhost:1234/v1",
    system_prompt=system_prompt
)

# client = OpenAI(
#     base_url="http://localhost:1234/v1",
#     api_key=os.environ["API_TOKEN"],
# )


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

def excHandler(f: callable):
    def wrapper():
        try:
            r = f()
            return r
        except Exception as e:
            return bot.chat(f"{e}")
    return wrapper

@On(bot, "spawn")
def spawn(*args):
    a.log("OK")
    bot.chat("Я появился")

@On(bot, "whisper")
def whisper(this, username: str, message: str, *args):
    bot.whisper(username, "Думаю над ответом...")
    response = model.ask(message)
    bot.whisper(username, response)