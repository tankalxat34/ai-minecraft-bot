import os
import sys
from javascript import require, On

from utils.dotenvLoader import loadDotEnv
from utils import cli
from utils.botUtils import BotActions, BotInventory
from ai import ai

loadDotEnv()

CMD = cli.Cli(" ".join(sys.argv))
USERNAME = CMD.getOption("name") or "_jeb"

mineflayer = require("mineflayer")
pathfinder = require("mineflayer-pathfinder")

bot = mineflayer.createBot({
    "host": os.environ.get("HOST") or CMD.getOption("host") or "127.0.0.1",
    "port": os.environ.get("PORT") or CMD.getOption("port") or "25565",
    "username": USERNAME,
    "version": os.environ.get("VERSION") or CMD.getOption("version") or CMD.getOption("v") or "1.20.4"
})

mcData = require("minecraft-data")(bot.version)

bot.loadPlugin(pathfinder.pathfinder)
movements = pathfinder.Movements(bot, mcData)
movements.canDig = False

botActions = BotActions(bot, movements)
botInventory = BotInventory(bot, mcData)


if not CMD.getOption("disableAi"):
    aisession = ai.AiSession(
        folder_id=os.environ.get("YAGPT_FOLDERID"), # type: ignore
        iam_token=ai.getIAMToken()["iamToken"],
        name=USERNAME,
        temperature=0.1,
        maxTokens=1000,
        generation_segment="latest"
    )
else:
    print("AI отключен")




@On(bot, "spawn")
def spawnHandler(*args):
    @On(bot, "chat")
    def chatHandler(this, username: str, message: str, *args):
        if username != USERNAME:
            bot.whisper(username, f"Напиши мне командой `/tell {USERNAME} <твое_сообщение>` и тогда я смогу помочь!")

    @On(bot, "whisper")
    def whisperHandler(this, username: str, message: str, *args):
        match message.lower():
            case "стоп":
                """Останаливает выполнение всех действий
                """
                botActions.reset()
                
                bot.whisper(username, "Есть остановиться!")

            case "за мной":
                botActions.reset()
                
                bot.whisper(username, "Уже иду!")
                player = bot.players[username]
                target = player.entity
                
                bot.pathfinder.setMovements(movements)
                bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 1), True)
                
            case _:
                # запрос в YaGPT, если не включена опция `disableAi`
                if CMD.getOption("disableAi"):
                    bot.chat("При запуске бота Вы отключили запросы к YandexGPT, указав необязательную опцию --disableAi.\n\nПожалуйста, перезапустите бота без использования этой опции")
                else:
                    try:
                        r = aisession.ask(message)
                        bot.whisper(username, f"{r}")
                    except Exception as e:
                        print(e)
                        bot.whisper(username, "Прости, не могу тебе ответить")
