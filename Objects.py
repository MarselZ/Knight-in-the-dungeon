""" Данный модуль отвечает за создание героя(Hero), союзников(Ally), противников(Enemy),
а также накладывает различные эффекты на героя(Effects)
"""


from abc import ABC, abstractmethod


class AbstractObject(ABC):
    def __init__(self):
        pass

    def draw(self, display):
        display.blit(self.sprite, ((self.position[0] - display.min_x)*display.game_engine.sprite_size,
                                   (self.position[1] - display.min_y)*display.game_engine.sprite_size))


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Enemy(Creature, Interactive):
    def __init__(self, icon, stats, xp, position):
        self.icon = icon
        self.stats = stats
        self.xp = xp
        self.position = position

    def interact(self, engine, hero):
        if self.stats["strength"] <= hero.stats["strength"]:
            hero.stats["strength"] += self.stats["strength"]
            hero.exp += self.xp
            engine.score += self.xp / 100
            if hero.exp >= 100 * (2 ** (hero.level - 1)):
                engine.notify(hero.level_up())
                
        else:
            for i in range(100):
                print(f'{i} - GAME OVER - ' * i)
            engine.working = False



class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp
        return f"level up! Now your level {self.level}"


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats['strength'] += 7
        self.stats['endurance'] += 7
        self.stats['luck'] += 7
        self.stats['intelligence'] -= 3
        self.hp += 50
       

class Blessing(Effect):
    def apply_effect(self):
        self.stats['strength'] += 2
        self.stats['endurance'] += 2
        self.stats['luck'] += 2
        self.stats['intelligence'] += 2
        

class Weakness(Effect):
    def apply_effect(self):
        self.stats['strength'] -= 4
        self.stats['endurance'] -= 4


