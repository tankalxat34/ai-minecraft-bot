import os
from javascript import require, On

from helper import loadDotEnv
from ai import ai

loadDotEnv()

mineflayer = require("mineflayer")
pathfinder = require("mineflayer-pathfinder")
GoalFollow = pathfinder.goals.GoalFollow

bot = mineflayer.createBot({
    "host": os.environ.get("HOST"),
    "port": os.environ.get("PORT"),
    "username": os.environ.get("BOT_USERNAME"),
    "version": "1.20.4"
})

bot.loadPlugin(pathfinder.pathfinder)

openaiSession = ai.Session()

@On(bot, "spawn")
def spawnHandler(*args):
    bot.chat(f"Привет всем! Меня зовут {os.environ.get("BOT_USERNAME")}")

    print(bot.version)

    mc_data = require("minecraft-data")(bot.version)
    movements = pathfinder.Movements(bot, mc_data)


    @On(bot, 'chat')
    def msgHandler(this, user: str, message: str, *args):
        if user != os.environ.get("BOT_USERNAME"):
            bot.chat("Думаю над ответом...")
            ai_model_response = openaiSession.ask(message).choices[0].message
            print(ai_model_response)
            bot.chat(str(ai_model_response))
            
            

        # if user != os.environ.get("BOT_USERNAME"):
        #     bot.chat(f"Привет {user}! Ты написал: {message}")
        #     if 'сюда' in message.lower():
        #         player = bot.players[user]
        #         target = player.entity

        #         bot.pathfinder.setMovements(movements)
        #         goal = GoalFollow(target, 1)
        #         bot.pathfinder.setGoal(goal, True)
        #     elif 'стоп' in message.lower():
        #         bot.pathfinder.stop()