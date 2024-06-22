"""Здесь описаны дополнительные методы для работы бота
"""

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
    def __init__(self, actionMap: dict[str, function], disableAi: bool = False) -> None:
        self.actionMap = actionMap
        self.disableAi = disableAi
        


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
    from javascript import require, On
    import json
    
    mcData = require("minecraft-data")("1.20.4")
    # foods = json.loads(json.dumps(mcData.foods))
    foods = (json.dumps(mcData.foods))
    print(foods)
    
    
