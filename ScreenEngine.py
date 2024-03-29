"""Данный модуль отвечает за отрисовку на экране всех основных элементов игры."""


import pygame
import collections
import Objects


colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):
    """Обработчик, передающий на отрисовку другим обработчикам по цепочкке."""

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])  # fill - это метод заполения у pygame.Surface

    def draw(self, canvas):  # нулевой обработчик отрисовки
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)  # blit создает на главном экране поверхности.
            self.successor.draw(canvas)

    def connect_engine(self, engine):  # нулевой обработчик движка
        if self.successor is not None:
            self.successor.connect_engine(engine) 
        

class GameSurface(ScreenHandle):
    """Обработчик для отрисовки основной(игровой части) экрана."""
            
    def draw_hero(self):
        self.game_engine.hero.draw(self)

    def draw_map(self):    
        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - self.min_x):
                for j in range(len(self.game_engine.map) - self.min_y):
                    self.blit(self.game_engine.map[self.min_y + j][self.min_x + i][0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw(self, canvas):
        # size = self.game_engine.sprite_size

        # расчет левого верхнего угла для сдвига карты, объектов и героя
        if self.game_engine.hero.position[0] * self.game_engine.sprite_size > 0.5 * self.get_width():
            self.min_x = self.game_engine.hero.position[0] -  int(0.5 * self.get_width() / self.game_engine.sprite_size)
        else:
            self.min_x = 0

        if self.game_engine.hero.position[1] * self.game_engine.sprite_size > 0.5 * self.get_height():
            self.min_y = self.game_engine.hero.position[1] - int(0.5 * self.get_height() / self.game_engine.sprite_size)
        else:
            self.min_y = 0

        self.draw_map()

        for obj in self.game_engine.objects:  # отрисовка объектов
            if isinstance(obj, Objects.Enemy):
                self.blit(obj.stats['sprite'][0], ((obj.position[0] - self.min_x) * self.game_engine.sprite_size,
                                      (obj.position[1] - self.min_y) * self.game_engine.sprite_size))
            elif isinstance(obj, Objects.Ally):
                self.blit(obj.sprite[0], ((obj.position[0] - self.min_x) * self.game_engine.sprite_size,
                                      (obj.position[1] - self.min_y) * self.game_engine.sprite_size))
            else:
                print(f'Объект: {obj} не может быть отрисован. Ошибка в: {__class__}')
                    
        self.draw_hero()
        super().draw(canvas)  # draw next surface in chain

    def connect_engine(self, engine):
        self.game_engine = engine  # save engine
        super().connect_engine(engine)  # send engine to next in chain


class ProgressBar(ScreenHandle):
    """обработчик для отрисовки показателей игры(HP, Exp, Gold, Str и других) на экране."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])    
    
    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))

        super().draw(canvas)  # draw next surface in chain

    def connect_engine(self, engine):  # save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(engine)


class InfoWindow(ScreenHandle):
    """Обработчик для отрисовки информационных сообщений на экране."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()
        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))

        super().draw(canvas) # draw next surface in chain  
    
    def connect_engine(self, engine):
        engine.subscribe(self)
        super().connect_engine(engine)
        

class HelpWindow(ScreenHandle):
    """Обработчик для отрисовки меню помощи на экране."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append(["DEATH", "HERO Strength must be < Enemy strength"])
        self.data.append(["→", "Move Right"])
        self.data.append(["←", "Move Left"])
        self.data.append(["↑", "Move Top"])
        self.data.append(["↓", "Move Bottom"])
        self.data.append(["H", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append(["R", "Restart Game"])
    
    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))
    
        super().draw(canvas)  # draw next surface in chain

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)
