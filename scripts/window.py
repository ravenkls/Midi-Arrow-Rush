import pygame


class Window:

    WINDOW_SIZE = 1280, 720

    def __init__(self, game):
        self.game = game

        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(self.game.__class__.__name__)

    def update(self):
        self.screen.fill((0, 0, 0))

    def render(self):
        pygame.display.update()