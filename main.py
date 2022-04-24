import pygame
from pathlib import Path
from functools import lru_cache

from scripts.input import InputManager
from scripts.window import Window
from scripts.arrows import ArrowsArea
from scripts.score import Score
from scripts.menu import Menu
from scripts.levellist import LevelList


class ArrowGame:

    FRAME_RATE = 60

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.click = pygame.mixer.Sound("data/sounds/click.wav")
        self.select = pygame.mixer.Sound("data/sounds/select.wav")

        self.accent_colour = (200, 55, 181)
        self.screen = "menu"

        self.clock = pygame.time.Clock()
        self.frame = 0

        self.data = Path("data")

        self.window = Window(self)
        self.input = InputManager(self)
        self.arrows_area = ArrowsArea(self)
        self.score = Score(self)
        self.menu = Menu(self)
        self.level_list = LevelList(self)

    @lru_cache
    def load_image(self, filename):
        return pygame.image.load(self.data / "images" / filename)

    def mainloop(self):
        while True:
            self.input.process_inputs()

            self.window.update()

            self.show_screen()

            self.window.render()

            self.clock.tick(self.FRAME_RATE)
            self.frame += 1

    def show_screen(self):
        if self.screen == "game":
            self.arrows_area.update(self.frame)
            self.arrows_area.render()
            self.score.update(self.frame)
            self.score.render()
        elif self.screen == "menu":
            self.menu.update(self.frame)
            self.menu.render()
        elif self.screen == "list":
            self.level_list.update(self.frame)
            self.level_list.render()

    def play_song(self, song_path, difficulty=0):
        self.screen = "game"
        self.arrows_area.song.load(song_path, difficulty)
        self.arrows_area.song.play()


if __name__ == "__main__":
    game = ArrowGame()
    game.mainloop()