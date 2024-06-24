"""Здесь описаны дополнительные методы для работы бота
"""
import difflib
import json
from typing import Callable
from uu import Error

from click import command

from ai import prompts
from ai.utils import createMessageBody

try:
    import ai.session
    import ai.utils
except ModuleNotFoundError:
    pass


def findByBestItem(slots: list[dict], fieldByMax: str, fieldByName: str = "") -> dict:
    """Найти лучший предмет в инвентаре по указанной характеристике.

    Args:
        fieldByMax (str): Наименование характеристики, значение которой является числом
        fieldByName (str): Часть значения поля `item.name`. Можно задать `sword` - тогда из инвентаря будет выбран лучший характеристике `fieldByMax` меч.
    
    Returns dict: json найденного предмета в инвентаре
    """
    item: dict = {f"{fieldByMax}": -1}
    for slot in slots:
        if slot and slot[fieldByMax] and (slot[fieldByMax] > item[fieldByMax] and (fieldByName.lower() in slot["name"].lower())):
            item = slot
    return item



class CommandsComparator:
    def __init__(self, casesMap: dict[str, Callable], aiSession: ai.session.YaGPTSession, disableAi: bool = False) -> None:
    # def __init__(self, casesMap: dict[str, Callable], aiSession, disableAi: bool = False) -> None:
        self.casesMap = casesMap
        self.disableAi = disableAi
        self.aiSession = aiSession
        
    def add(self, command: str, f: Callable):
        """Добавляет действие в список действий

        Args:
            command (str): Словесное и краткое название команды (например: `за мной`, `стоп` и т.д.)
            aiSession (ai.AiSession): Экземпляр сессии с YandexGPT. От имени этой сессии будет осуществляться запрос к нейросети
            f (function): Функция, вызывающаяся при совпадении команды игрока в чате с заданной здесь командой
        """
        self.casesMap[command.lower()] = f
        
    def compare(self, commandFromGame: str) -> Callable:
        """Сравнивает полученную команду в чате игры с одним из заданных в компараторе кейсов. 
        
        Сравнение происходит через YandexGPT, поэтому бот должен быть запущен со включенными нейросетевыми возможностями (т.е. без опции `disableAi`).

        Args:
            commandFromGame (str): Сообщение игрока в чате игры с командой для бота

        Returns:
            Callable: Функцию, вызывав которую бот начнет выполнять запрашиваемое действие
        """
        userCommand = commandFromGame.lower()
        if userCommand in self.casesMap.keys():
            return self.casesMap[userCommand]
        
        if self.disableAi:
            raise Error("Отключены нейросетевые возможности, сравнение невозможно")
        
        commands = list(self.casesMap.keys())
        strCommands = f'[{", ".join(commands)}]'
        # matches = difflib.get_close_matches(userCommand, commands, n=1, cutoff=0.65)
        
        # if matches and matches[0] in commands:
        #     return self.casesMap[matches[0]]
        # else:
        formattedSystemPrompt = prompts.Prompts.SYSTEM_PROMPT_2.replace("{commands}", strCommands)
        messages = [
            createMessageBody(formattedSystemPrompt, "system"),
            createMessageBody(userCommand, "user"),
        ]
        print(messages)
        aiResponse: dict[str, str] = json.loads(self.aiSession.customAsk(messages, temperature=0.35))
        """Структура вида:
        ```
        {
            "result": слово_из_перечня_либо_null, 
            "creative": твой_креативный_ответ_либо_null
        }
        ```
        """
        
        # возвращаем креативный ответ всегда, а кейс выполняем тут же, если это возможно
        print(aiResponse)
        try:
            print("Выполнил кейс", aiResponse["result"])
            self.casesMap[aiResponse["result"]]()
        except KeyError:
            pass
        return lambda: aiResponse["creative"]

        
        

class BotActions:
    def __init__(self, bot, movements):
        """Дополнительные методы для управления ботом

        Args:
            bot (`mineflayer.createBot`): Экземпляр бота
            movements (`pathfinder.Movements`): Двигатель для бота
        """
        
        self.bot = bot
        self.movements = movements
        
    def reset(self):
        """Сбросить все действия для текущего бота
        """
        self.bot.pathfinder.setGoal(None)
        self.bot.pathfinder.setMovements(self.movements)
        self.bot.stopDigging()
        
        
class BotInventory:
    def __init__(self, bot, mcData) -> None:
        self.bot = bot
        self.mcData = mcData
        self.inventory = self.bot.inventory
        self.slots: list = self.bot.inventory.slots
    
    @property
    def nslots(self):
        return list(filter(lambda x: bool(x), self.slots))
    
    @property
    def hotbar(self, index: int = 0) -> dict:
        return filter(lambda d: d.slot == 36 + index, self.slots) # type: ignore
    
    def __contains__(self, itemIdOrName: int | str) -> bool:
        """Проверить наличие предмета в инвентаре бота

        Args:
            itemIdOrName (int | str): ID или системное имя предмета

        Returns:
            bool: True, если указанный предмет есть в инвентаре бота
        """
        for slot in self.slots:
            if slot and (itemIdOrName == slot.type or itemIdOrName == slot.name.lower() or itemIdOrName in slot.name.lower()):
                return True
        return False
    
    def _findByBestItem(self, fieldByMax: str, fieldByName: str = "") -> dict:
        """Найти лучший предмет в инвентаре по указанной характеристике.

        Args:
            fieldByMax (str): Наименование характеристики, значение которой является числом
            fieldByName (str): Часть значения поля `item.name`. Можно задать `sword` - тогда из инвентаря будет выбран лучший по заданной характеристике меч.
        
        Returns dict: json найденного предмета в инвентаре
        """
        return findByBestItem(self.slots, fieldByMax=fieldByMax, fieldByName=fieldByName)
    
    def hasPickaxe(self) -> dict:
        """Проверить наличие кирки. Если кирка есть - вернуть json самой лучшей кирки

        Returns:
            dict: json самой лучшей кирки в инвентаре
        """
        return {}
    
    
if __name__ == "__main__":
    comparator = CommandsComparator({
        "стоп": lambda x: print("Вызвана функция `стоп`"),
        "за мной": lambda x: print("Вызвана функция `за мной`"),
        "найди алмазы": lambda x: print("Вызвана функция `найди алмазы`"),
        "добудь дерево": lambda x: print("Вызвана функция `добудь дерево`"),
    }, None) # type: ignore

    comparator.compare("стой")