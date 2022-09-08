"""Данный модуль выполняет обслуживающие функции. Осуществляет создание начальных параметров игры,
восстановления здоровья, применение blessing и berserk, снятие эффектов с героя, действие при взятии сундука,
а также создание карт игры.
"""

import pygame
import random
import os
import yaml
import Objects


OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


def create_sprite(img, sprite_size):
    """Возвращается поверхность изображения в виде иконки."""
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


def reload_game(engine, hero):
    """Создание начальных параметров игры"""
    global level_list
    level_list_max = len(level_list) - 1
    engine.level += 1
    hero.position = [1, 1]
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'].get_map()  # вызов карты
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))
    engine.add_hero(hero)


def restore_hp(engine, hero):
    """Восстановление здоровья"""
    engine.score += 0.1
    hero.hp = hero.max_hp
    engine.notify("HP restored")


def apply_blessing(engine, hero):
    """Применение blessing и berserk"""
    if hero.gold >= int(20 * 1.5 ** engine.level) - 2 * hero.stats["intelligence"]:
        engine.score += 0.2
        hero.gold -= int(20 * 1.5 ** engine.level) - 2 * hero.stats["intelligence"]
        if random.randint(0, 1) == 0:
            engine.hero = Objects.Blessing(hero)
            engine.notify("Blessing applied")
        else:
            engine.hero = Objects.Berserk(hero)
            engine.notify("Berserk applied")
    else:
        engine.score -= 0.1


def remove_effect(engine, hero):
    """Снятие эффектов"""
    if hero.gold >= int(10 * 1.5 ** engine.level) - 2 * hero.stats["intelligence"] and "base" in dir(hero):
        hero.gold -= int(10 * 1.5 ** engine.level) - \
                     2 * hero.stats["intelligence"]
        engine.hero = hero.base
        engine.hero.calc_max_HP()
        engine.notify("Effect removed")


def add_gold(engine, hero):
    """Взятие сундука"""
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1 ** (engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


class MapFactory(yaml.YAMLObject):
    """Базовый класс создания карт"""

    @classmethod
    def from_yaml(cls, loader, node):
        _map = cls.Map()
        _odj = cls.Objects()
        config = loader.construct_mapping(node)
        _odj.config.update(config)
        return {'map': _map, 'obj': _odj}


class EndMap(MapFactory):
    """Создание карты окончания игры"""

    yaml_tag = "!end_map"

    class Map:
        def __init__(self):
            self.Map = ['000000000000000000000000000000000000000',
                        '0                                     0',
                        '0                                     0',
                        '0  0   0   000   0   0  00000  0   0  0',
                        '0  0  0   0   0  0   0  0      0   0  0',
                        '0  000    0   0  00000  0000   0   0  0',
                        '0  0  0   0   0  0   0  0      0   0  0',
                        '0  0   0   000   0   0  00000  00000  0',
                        '0                                   0 0',
                        '0                                     0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    """Создание случайной карты"""

    yaml_tag = "!random_map"

    class Map:

        def __init__(self):
            self.Map = [[0 for _ in range(41)] for _ in range(41)]
            for i in range(41):
                for j in range(41):
                    if i == 0 or j == 0 or i == 40 or j == 40:
                        self.Map[j][i] = wall
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, 39), random.randint(1, 39))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, 39), random.randint(1, 39))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(random.randint(0, 5)):
                    coord = (random.randint(1, 30), random.randint(1, 22))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


class EmptyMap(MapFactory):
    """Создание пустой карты"""

    yaml_tag = '!empty_map'

    class Map:

        def __init__(self):
            self.Map = [[0 for _ in range(11)] for _ in range(11)]
            for i in range(11):
                for j in range(11):
                    if i == 0 or j == 0 or i == 10 or j == 10:
                        self.Map[j][i] = wall
                    else:
                        self.Map[j][i] = floor1

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, 9), random.randint(1, 9))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 9),
                                     random.randint(1, 9))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 9),
                                         random.randint(1, 9))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))
            return self.objects


class SpecialMap(MapFactory):
    """Создание спец. карты"""

    yaml_tag = '!special_map'

    class Map:
        def __init__(self):
            self.Map = ['000000000000000000000000000000000000000',
                        '0                                     0',
                        '0                                     0',
                        '0         0    0         0    0       0',
                        '0        0      0       0      0      0',
                        '0  00   0        0 00  0        0 00  0',
                        '0        0      0       0      0      0',
                        '0         0    0         0    0       0',
                        '0                                     0',
                        '0                                     0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, 37), random.randint(1, 9))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 37),
                                     random.randint(1, 9))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 37),
                                         random.randint(1, 9))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for enemy, count in self.config.items():
                for i in range(count):
                    prop = object_list_prob['enemies'][enemy]
                    coord = (random.randint(1, 37), random.randint(1, 9))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:  # проверка координат на совпадение со стеной
                            intersect = True
                            coord = (random.randint(1, 37),
                                     random.randint(1, 9))
                            continue
                        for obj in self.objects:  # проверка координат на совпадение с другими объектами или героем
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 37),
                                         random.randint(1, 9))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


class MyMap(MapFactory):
    """Создание дополнительной карты"""

    yaml_tag = '!my_map'

    class Map:

        def __init__(self):
            self.Map = ['000000000000000000000000000000000000000',
                        '0  0             0                    0',
                        '0  0  00000  0  00                    0',
                        '0  0  0     0  00   0  00000   00000  0',
                        '0  0  0   0    0  0   0        0   0  0',
                        '0     00000    0  0000000000   0   0  0',
                        '0  0     0     0  000          0   0  0',
                        '0  0000  0 00000  00000000000000   0  0',
                        '0     0     0          0  0           0',
                        '0  0  0     0  000000000  0  0        0',
                        '0  0  0     0  0       0  0  0        0',
                        '0  0  0     0  0    00 0  0  0        0',
                        '0  0  0000  0  0000000 0  0  0        0',
                        '0  0     0 00          0     0        0',
                        '0  00000    0000000000000000000 0000000',
                        '0      0000     0             0    0  0',
                        '0      0        0       00000 0       0',
                        '0      0  000000000  000      000000  0',
                        '0                       00000         0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):

            prop = object_list_prob['objects']['stairs']
            coord = (16, 11)
            self.objects.append(Objects.Ally(
                prop['sprite'], prop['action'], coord))

            prop = object_list_prob['ally']['gin']
            coord = (2, 2)
            self.objects.append(Objects.Ally(
                prop['sprite'], prop['action'], coord))

            prop = object_list_prob['enemies']['hydra']
            coord = (20, 10)
            self.objects.append(Objects.Enemy(
                prop['sprite'], prop, prop['experience'], coord))

            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(random.randint(0, 5)):
                    coord = (random.randint(1, 37), random.randint(1, 18))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, 37),
                                     random.randint(1, 18))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 37),
                                         random.randint(1, 18))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


wall = [0]
floor1 = [0]
floor2 = [0]
floor3 = [0]


def service_init(sprite_size, full=True):
    """Инициализация обслуживающих параметров"""
    global object_list_prob, level_list
    global wall
    global floor1
    global floor2
    global floor3

    wall[0] = create_sprite(os.path.join("texture", "wall.png"), sprite_size)
    floor1[0] = create_sprite(os.path.join("texture", "Ground_1.png"), sprite_size)
    floor2[0] = create_sprite(os.path.join("texture", "Ground_2.png"), sprite_size)
    floor3[0] = create_sprite(os.path.join("texture", "Ground_3.png"), sprite_size)

    file = open("objects.yml", "r")

    object_list_tmp = yaml.load(file.read())
    if full:
        object_list_prob = object_list_tmp

    object_list_actions = {'reload_game': reload_game,
                           'add_gold': add_gold,
                           'apply_blessing': apply_blessing,
                           'remove_effect': remove_effect,
                           'restore_hp': restore_hp}

    for obj in object_list_prob['objects']:
        prop = object_list_prob['objects'][obj]
        prop_tmp = object_list_tmp['objects'][obj]
        prop['sprite'][0] = create_sprite(
            os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for ally in object_list_prob['ally']:
        prop = object_list_prob['ally'][ally]
        prop_tmp = object_list_tmp['ally'][ally]
        prop['sprite'][0] = create_sprite(
            os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for enemy in object_list_prob['enemies']:
        prop = object_list_prob['enemies'][enemy]
        prop_tmp = object_list_tmp['enemies'][enemy]
        prop['sprite'][0] = create_sprite(
            os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)

    file.close()

    if full:
        file = open("levels.yml", "r")
        level_list = yaml.load(file.read())['levels']
        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
        file.close()
