import os
import sys
from javascript import require, On

from utils.dotenvLoader import loadDotEnv
from utils import cli
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

MC_DATA = require("minecraft-data")(bot.version)

bot.loadPlugin(pathfinder.pathfinder)

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

    movements = pathfinder.Movements(bot, MC_DATA)

    @On(bot, "chat")
    def chatHandler(this, username: str, message: str, *args):
        if username != USERNAME:
            bot.whisper(username, f"Не люблю общаться в общем чате. Напиши мне командой `/tell {USERNAME} <твое_сообщение>` и тогда я смогу помочь!")

    @On(bot, "whisper")
    def whisperHandler(this, username: str, message: str, *args):
        match message.lower():
            case "за мной":
                bot.pathfinder.stop()
                bot.pathfinder.setMovements(movements)
                
                
                bot.whisper(username, "Уже иду!")
                player = bot.players[username]
                target = player.entity
                
                bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 1), True)
            case "стоп":
                bot.pathfinder.stop()
                bot.pathfinder.setMovements(movements)
                
                bot.whisper(username, "Есть остановиться!")
                # bot.whisper(username, "Остановился")
                # bot.whisper(username, aisession.ask(f"Ответ на это сообщение ниже пожалуйста сгенерируй исходя из того, что ты прекратил выполнять какие то действия внутри Minecraft:\n\n{message}"))
            case "алмазы":
                bot.pathfinder.stop()
                bot.pathfinder.setMovements(movements)
                
                block = bot.findBlock({
                    "matching": MC_DATA.blocksByName.diamond_ore.id,
                    "maxDistance": 256
                })
                print(block.position)
                if not block:
                    bot.whisper(username, "Не нашел алмазной руды!")
                else:
                    bot.pathfinder.setGoal(pathfinder.goals.GoalBlock(block.position.x, block.position.y + 1, block.position.z), True)
            case _:
                # запрос в YaGPT, если не включена опция об отключении AI
                if CMD.getOption("disableAi"):
                    bot.whisper(username, "Типа сделан запрос в YaGPT")
                else:
                    try:
                        r = aisession.ask(message)
                        bot.whisper(username, f"{r}")
                    except Exception as e:
                        print(e)
                        bot.whisper(username, "Прости, я задумался и забыл, что хотел тебе ответить")

