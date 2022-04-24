import pygame


class Score:
    def __init__(self, game):
        self.game = game

        self._animation_from_score = 0
        self._animation_to_score = 0
        self._score = 0
        self._streak = 0
        self.max_streak = 0

        self.width = 400
        self.height = 180

        self.score_font_size = 50
        self.streak_font_size = 15
        self.font_family = self.game.data / "fonts" / "Oswald-Regular.ttf"

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

        self.rect.x = self.game.window.WINDOW_SIZE[0] // 2 - self.width // 2

        self.image.set_colorkey((0, 0, 0))

    @property
    def value(self):
        return self._animation_to_score

    @value.setter
    def value(self, val):
        self._animation_to_score = val
        self._animation_from_score = self._score

    @property
    def streak(self):
        return self._streak

    @streak.setter
    def streak(self, val):
        self._streak = val
        if self._streak > self.max_streak:
            self.max_streak = val

    def update(self, frame):
        if self._animation_to_score != int(self._score):
            distance = self._animation_to_score - self._score
            step = distance / 60
            self._score += step
            if (
                self._animation_to_score - 0.1
                < self._score
                < self._animation_to_score + 0.1
            ):
                self._score = self._animation_to_score

    def render(self):
        self.image.fill((0, 0, 0))

        score_font = pygame.font.Font(self.font_family, self.score_font_size)
        streak_font = pygame.font.Font(self.font_family, self.streak_font_size)

        score_surface = score_font.render(str(int(self._score)), True, (255, 255, 255))
        streak_surface = streak_font.render(
            "Streak: " + str(self.streak) + "  |  Max Streak: " + str(self.max_streak),
            True,
            (255, 255, 255),
        )

        self.image.blit(
            streak_surface,
            (
                self.width // 2 - streak_surface.get_width() // 2,
                self.height // 2 + score_surface.get_height() // 2,
            ),
        )

        self.image.blit(
            score_surface,
            (
                self.width // 2 - score_surface.get_width() // 2,
                self.height // 2 - score_surface.get_height() // 2,
            ),
        )

        self.game.window.screen.blit(self.image, self.rect)