import pygame
import json


class LevelList:
    def __init__(self, game):
        self.game = game

        self.width, self.height = self.game.window.WINDOW_SIZE
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

        self.selected_song = 0
        self.song_selected = False

        self.margin_x, self.margin_y = 100, 50

        self.title_font = pygame.font.Font(
            self.game.data / "fonts" / "Oswald-Regular.ttf", 40
        )
        self.title_surface = self.title_font.render("LEVEL LIST", True, (255, 255, 255))

        self.info_screen = InfoScreen(self)

        self.levels = []

        self.song_paths = list((self.game.data / "songs").glob("*.json"))

        for json_file in self.song_paths:
            with json_file.open() as f:
                self.levels.append(json.load(f))

    def move_up(self):
        if not self.song_selected:
            if self.selected_song > 0:
                self.selected_song -= 1
        else:
            if self.info_screen.selected_difficulty > 0:
                self.info_screen.selected_difficulty -= 1

    def move_down(self):
        if not self.song_selected:
            if self.selected_song < len(self.levels) - 1:
                self.selected_song += 1
        else:
            if (
                self.info_screen.selected_difficulty
                < len(self.levels[self.selected_song]["levels"]) - 1
            ):
                self.info_screen.selected_difficulty += 1

    def select(self):
        if not self.song_selected:
            self.song_selected = True
            self.info_screen.selected_difficulty = 0
        else:
            self.game.play_song(
                self.song_paths[self.selected_song],
                self.info_screen.selected_difficulty,
            )

    def back(self):
        if self.song_selected:
            self.song_selected = False
            self.info_screen.selected_difficulty = None
        else:
            self.game.screen = "menu"

    def update(self, frame):
        pass

    def render(self):
        self.image.fill((0, 0, 0))

        self.image.blit(
            self.title_surface,
            (
                self.margin_x,
                self.margin_y,
            ),
        )

        for i, level in enumerate(self.levels):
            btn = LevelButton(self, level)
            if i == self.selected_song:
                btn.selected = True
            btn_surface = btn.render()
            self.image.blit(
                btn_surface,
                (
                    self.margin_x,
                    self.margin_y
                    + self.title_surface.get_height()
                    + 20
                    + i * (btn_surface.get_height() + 10),
                ),
            )

        self.info_screen.update()
        self.info_screen.render()

        self.game.window.screen.blit(self.image, self.rect)


class LevelButton:
    def __init__(self, level_list, level):
        self.level_list = level_list
        self.level = level
        self.selected = False
        self.image = pygame.Surface(
            (
                (self.level_list.image.get_width() - self.level_list.margin_x * 2)
                * 0.55,
                50,
            ),
            pygame.SRCALPHA,
        )
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

        self.title_font = pygame.font.Font(
            self.level_list.game.data / "fonts" / "Oswald-Regular.ttf", 20
        )

    def update(self):
        pass

    def render(self):
        if self.selected:
            self.image.fill(self.level_list.game.accent_colour)
        else:
            self.image.fill((26, 26, 26))

        title_surface = self.title_font.render(
            self.level.get("artist", "Unknown")
            + " - "
            + self.level.get("name", "Unknown"),
            True,
            (255, 255, 255),
        )
        self.image.blit(
            title_surface,
            (
                15,
                self.image.get_height() // 2 - title_surface.get_height() // 2,
            ),
        )

        return self.image


class InfoScreen:
    def __init__(self, level_list):
        self.level_list = level_list
        self.margin_x = 25
        self.margin_y = 25

        self.selected_difficulty = None

        self.difficulties = [
            "Easy",
            "Medium",
            "Hard",
            "Harder",
            "Very Hard",
            "Extremely Hard",
            "Borderline Impossible",
            "Impossible",
            "Definitely Impossible",
        ]

        self.image = pygame.Surface(
            (
                (self.level_list.image.get_width() - self.level_list.margin_x * 2)
                * 0.43,
                self.level_list.image.get_height()
                - self.level_list.margin_y * 2
                - self.level_list.title_surface.get_height()
                - 20,
            ),
            pygame.SRCALPHA,
        )

        self.song_font = pygame.font.Font(
            self.level_list.game.data / "fonts" / "Oswald-Regular.ttf", 25
        )
        self.artist_font = pygame.font.Font(
            self.level_list.game.data / "fonts" / "Oswald-Regular.ttf", 15
        )
        self.section_header_font = pygame.font.Font(
            self.level_list.game.data / "fonts" / "Oswald-Regular.ttf", 15
        )

        self.rect = self.image.get_rect()
        self.rect.x = (
            self.level_list.image.get_width() - self.level_list.margin_x * 2
        ) * 0.57 + self.level_list.margin_x
        self.rect.y = (
            self.level_list.margin_y + self.level_list.title_surface.get_height() + 20
        )

    def update(self):
        pass

    def render(self):
        self.image.fill((255, 255, 255))

        artist_surface = self.artist_font.render(
            self.level_list.levels[self.level_list.selected_song].get(
                "artist", "Unknown"
            ),
            True,
            (0, 0, 0),
        )

        song_surface = self.song_font.render(
            self.level_list.levels[self.level_list.selected_song].get(
                "name", "Unknown"
            ),
            True,
            (0, 0, 0),
        )

        section_header_surface = self.section_header_font.render(
            "DIFFICULTY LEVELS", True, (0, 0, 0)
        )

        self.image.blit(
            artist_surface,
            (
                self.margin_x,
                self.margin_y,
            ),
        )

        self.image.blit(
            song_surface,
            (
                self.margin_x,
                self.margin_y + artist_surface.get_height(),
            ),
        )

        self.image.blit(
            section_header_surface,
            (
                self.margin_x,
                self.margin_y
                + artist_surface.get_height()
                + song_surface.get_height()
                + 30,
            ),
        )

        for i, (level, difficulty) in enumerate(
            zip(
                self.level_list.levels[self.level_list.selected_song]["levels"],
                self.difficulties,
            )
        ):
            btn = DifficultyButton(self, i)
            if i == self.selected_difficulty:
                btn.selected = True
            btn_surface = btn.render()
            self.image.blit(
                btn_surface,
                (
                    self.margin_x,
                    self.margin_y
                    + artist_surface.get_height()
                    + song_surface.get_height()
                    + section_header_surface.get_height()
                    + 40
                    + i * (btn_surface.get_height() + 7),
                ),
            )

        self.level_list.image.blit(self.image, self.rect)


class DifficultyButton:
    def __init__(self, info_screen, level):
        self.info_screen = info_screen
        self.level = level
        self.selected = False
        self.image = pygame.Surface(
            (
                (self.info_screen.image.get_width() - self.info_screen.margin_x * 2),
                35,
            ),
            pygame.SRCALPHA,
        )
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

        self.title_font = pygame.font.Font(
            self.info_screen.level_list.game.data / "fonts" / "Oswald-Regular.ttf", 15
        )

    def update(self):
        pass

    def render(self):
        if self.selected:
            self.image.fill(self.info_screen.level_list.game.accent_colour)
        else:
            self.image.fill((230, 230, 230))

        title_surface = self.title_font.render(
            self.info_screen.difficulties[self.level],
            True,
            (255, 255, 255) if self.selected else (1, 1, 1),
        )
        self.image.blit(
            title_surface,
            (
                15,
                self.image.get_height() // 2 - title_surface.get_height() // 2,
            ),
        )

        return self.image