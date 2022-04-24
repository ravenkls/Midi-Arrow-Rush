import pygame
import math


class Menu:
    def __init__(self, game):
        self.game = game
        self.subtitle_opacity = 1

        self.width, self.height = self.game.window.WINDOW_SIZE
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

        self.title_font = pygame.font.Font(
            self.game.data / "fonts" / "Oswald-Regular.ttf", 52
        )
        self.subtitle_font = pygame.font.Font(
            self.game.data / "fonts" / "Oswald-Regular.ttf", 16
        )

    def update(self, frame):
        self.subtitle_opacity = ((math.cos(frame / 20) + 1) / 2) * 255

    def render(self):
        self.image.fill((0, 0, 0))
        title_surface = self.title_font.render("MIDI ARROW RUSH", True, (255, 255, 255))
        subtitle_surface = self.subtitle_font.render(
            "Press and key to continue", True, self.game.accent_colour
        )
        subtitle_surface.set_alpha(self.subtitle_opacity)

        self.image.blit(
            title_surface,
            (
                self.image.get_width() // 2 - title_surface.get_width() // 2,
                self.image.get_height() // 2 - title_surface.get_height() // 2 - 25,
            ),
        )

        self.image.blit(
            subtitle_surface,
            (
                self.image.get_width() // 2 - subtitle_surface.get_width() // 2,
                self.image.get_height() // 2 - subtitle_surface.get_height() // 2 + 25,
            ),
        )

        self.game.window.screen.blit(self.image, self.rect)