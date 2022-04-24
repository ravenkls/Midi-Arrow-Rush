import json
from collections import defaultdict

import pygame
import math

from .midi import MidiFile
from functools import lru_cache


class ArrowsArea:
    def __init__(self, game):
        self.game = game
        self.arrow_size = (75, 75)

        self.starting_frame = None

        self.width = 450
        self.height = self.game.window.WINDOW_SIZE[1]

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = self.game.window.WINDOW_SIZE[0] // 2 - self.width // 2

        self.controls = Controls(self)
        self.song = Song(self)

    def reset(self):
        self.starting_frame = None
        self.controls = Controls(self)
        self.song.stop()
        self.song = Song(self)

    def update(self, frame):
        if self.starting_frame is None:
            self.starting_frame = frame
        self.controls.update(frame - self.starting_frame)
        self.song.update(frame - self.starting_frame)

    def render(self):
        self.image.fill((0, 0, 0))

        self.controls.render()
        self.song.render()

        self.game.window.screen.blit(self.image, self.rect)

    def get_x_pos_by_group(self, group):
        spacing = self.width // 4
        x = spacing // 2 + group * spacing - self.arrow_size[0] // 2
        return x

    @lru_cache
    def arrow_image_by_group(self, group):
        arrow_images = ["left.png", "up.png", "down.png", "right.png"]
        arrow_image = pygame.transform.scale(
            self.game.load_image(arrow_images[group]), self.arrow_size
        ).convert_alpha()
        return arrow_image


class Controls:
    def __init__(self, arrows_area):
        self.arrows_area = arrows_area
        self.controls_y = 200
        self.glow_size = 13

        self.glow_images = {}
        self.glowing_groups = []
        self.stop_glowing = []

        # CONTROL IMAGES
        self.up_arrow = pygame.transform.scale(
            self.arrows_area.game.load_image("upo.png"),
            self.arrows_area.arrow_size,
        ).convert_alpha()

        self.down_arrow = pygame.transform.scale(
            self.arrows_area.game.load_image("downo.png"),
            self.arrows_area.arrow_size,
        ).convert_alpha()

        self.left_arrow = pygame.transform.scale(
            self.arrows_area.game.load_image("lefto.png"),
            self.arrows_area.arrow_size,
        ).convert_alpha()

        self.right_arrow = pygame.transform.scale(
            self.arrows_area.game.load_image("righto.png"),
            self.arrows_area.arrow_size,
        ).convert_alpha()

        # GLOW IMAGES
        self.up_glow = pygame.transform.scale(
            self.arrows_area.game.load_image("upg.png"),
            (
                self.arrows_area.arrow_size[0] + self.glow_size,
                self.arrows_area.arrow_size[1] + self.glow_size,
            ),
        ).convert_alpha()

        self.down_glow = pygame.transform.scale(
            self.arrows_area.game.load_image("downg.png"),
            (
                self.arrows_area.arrow_size[0] + self.glow_size,
                self.arrows_area.arrow_size[1] + self.glow_size,
            ),
        ).convert_alpha()

        self.left_glow = pygame.transform.scale(
            self.arrows_area.game.load_image("leftg.png"),
            (
                self.arrows_area.arrow_size[0] + self.glow_size,
                self.arrows_area.arrow_size[1] + self.glow_size,
            ),
        ).convert_alpha()

        self.right_glow = pygame.transform.scale(
            self.arrows_area.game.load_image("rightg.png"),
            (
                self.arrows_area.arrow_size[0] + self.glow_size,
                self.arrows_area.arrow_size[1] + self.glow_size,
            ),
        ).convert_alpha()

    def glow(self, group):
        self.glowing_groups.append(group)

    def stop_glow(self, group):
        if not any(i[0] == i for i in self.stop_glowing):
            self.stop_glowing.append([group, 1])

    def update(self, frame):
        glows = (self.left_glow, self.up_glow, self.down_glow, self.right_glow)
        for g in self.glowing_groups:
            image = glows[g].copy()
            alpha = 160 + (math.sin(0.5 * frame) + 1) * 30

            for i in range(len(self.stop_glowing)):
                if self.stop_glowing[i][0] == g:
                    self.stop_glowing[i][1] -= 0.05
                    if self.stop_glowing[i][1] <= 0:
                        try:
                            self.glowing_groups.remove(self.stop_glowing[i][0])
                            self.glow_images.pop(self.stop_glowing[i][0])
                            self.stop_glowing.remove(self.stop_glowing[i])
                        except (ValueError, KeyError):
                            pass
                        return
                    alpha = int(alpha * self.stop_glowing[i][1])
                    break

            image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            self.glow_images[g] = image

    def render(self):
        arrows = (self.left_arrow, self.up_arrow, self.down_arrow, self.right_arrow)

        for n, image in self.glow_images.items():
            x = self.arrows_area.get_x_pos_by_group(n)
            self.arrows_area.image.blit(
                image, (x - self.glow_size // 2, self.controls_y - self.glow_size // 2)
            )

        for n, arrow in enumerate(arrows):
            x = self.arrows_area.get_x_pos_by_group(n)
            self.arrows_area.image.blit(arrow, (x, self.controls_y))


class Song:
    def __init__(self, arrows_area):
        self.arrows_area = arrows_area
        self.playing = False
        self.frame = 0
        self.start_frame = 0
        self.playing_instruments = []
        self.song_name = ""
        self.song_artist = ""

    def load(self, song_file, difficulty=0):
        with open(song_file) as f:
            song_data = json.load(f)
        self.song_name = song_data.get("name", "Unknown")
        self.song_artist = song_data.get("artist", "Unknown")
        self.song = MidiFile(
            song_file.parent / song_data["midi"], tempo=song_data.get("tempo", 1)
        )
        self.song.intro(3)
        self.song.initialise_player()
        self.playing_instruments = self.song.get_instruments_by_index(
            *song_data["levels"][difficulty]
        )
        self.arrows = []
        self.frequencies = [
            n.note
            for n in sorted(
                [
                    n
                    for i, notes in self.song.notes.items()
                    for n in notes
                    if i in self.playing_instruments
                ],
                key=lambda x: x.note,
            )
        ]

        # load arrows
        arrow_notes = [
            n
            for instrument, notes in self.song.notes.items()
            for n in notes
            if instrument in self.playing_instruments
        ]
        arrow_notes_by_time = defaultdict(list)
        for note in arrow_notes:
            arrow_notes_by_time[note.time].append(note)

        for time, notes_group in arrow_notes_by_time.items():
            self.arrows.append(Arrow(self, notes_group))

    def get_group_by_note(self, notes):
        step = (len(self.frequencies) - 1) // 4
        group = 0
        avg_note = sum(n.note for n in notes) / len(notes)
        for i in range(step, step * 3 + 1, step):
            if avg_note > self.frequencies[i]:
                group += 1
            else:
                break
        return group

    def get_playable_arrows(self):
        return [a for a in self.arrows if a.is_playable()]

    def play(self):
        self.playing = True
        self.start_frame = self.frame

    def stop(self):
        self.playing = False

    @property
    def song_frame(self):
        return self.frame - self.start_frame

    def update(self, frame):
        self.frame = frame

        if self.playing:
            for instrument, notes in self.song.notes.items():
                if instrument not in self.playing_instruments:
                    for note in notes:
                        note.update(self.song_frame)

            for arrow in self.arrows:
                arrow.update(self.song_frame)

    def render(self):
        name_font = pygame.font.Font(
            self.arrows_area.game.data / "fonts" / "Oswald-Regular.ttf", 20
        )

        name_surface = name_font.render(
            " ".join(f"{self.song_name} | {self.song_artist}".upper()),
            True,
            (255, 255, 255),
        )

        for arrow in reversed(self.arrows):
            arrow.render()

        self.arrows_area.game.window.screen.blit(
            name_surface,
            (
                self.arrows_area.game.window.screen.get_width() // 2
                - name_surface.get_width() // 2,
                self.arrows_area.game.window.screen.get_height()
                - name_surface.get_height()
                - 20,
            ),
        )


class Arrow:

    SPEED = 5
    PLAY_RANGE = 75
    ENLARGE_SIZE = 20

    def __init__(self, song, notes):
        self.song = song
        self.notes = notes
        self.time = self.notes[0].time
        self.duration = max(n.duration for n in self.notes)
        self.finished = False
        self.grow_center = None

        self._opacity = 255

        self.group = self.song.get_group_by_note(self.notes)

        self.target_pos = self.song.arrows_area.controls.controls_y

        self.image = self.song.arrows_area.arrow_image_by_group(self.group)
        self.image_copy = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = self.song.arrows_area.get_x_pos_by_group(self.group)
        self.rect.y = self.target_pos + self.time * self.SPEED

        self.playing = False

    def is_playable(self):
        return (
            self.target_pos - self.PLAY_RANGE // 2
            < self.rect.y
            < self.target_pos + self.PLAY_RANGE // 2
            and not self.playing
        )

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        if val < 0:
            val = 0
        elif val > 255:
            val = 255

        if self.opacity != val:
            self.image = self.image_copy.copy()
            self.image.fill((255, 255, 255, val), None, pygame.BLEND_RGBA_MULT)

        self._opacity = val

    def update(self, frame):
        if self.playing:
            for n in self.notes:
                n.update(self.song.song_frame)
            if self.grow_center is None:
                self.rect.y = self.target_pos
            if all(n.finished for n in self.notes) and not self.finished:
                self.song.arrows_area.controls.stop_glow(self.group)
                self.finished = True
        else:
            self.rect.y -= self.SPEED
            if (
                self.rect.y < self.target_pos - self.PLAY_RANGE // 2
                and not self.finished
            ):
                self.song.arrows_area.game.score.streak = 0
                self.finished = True

        if not self.finished:
            if self.rect.y < 600 and self.opacity < 230:
                self.opacity += 16
            elif self.rect.y > 600:
                self.opacity = 0

    def render(self):
        if (
            not self.playing
            and 0 < self.rect.y < self.song.arrows_area.height
            or (self.playing and not self.song.song_frame > self.time + self.duration)
        ):
            self.song.arrows_area.image.blit(self.image, self.rect)

        elif self.song.song_frame > self.time + self.duration and self.opacity > 0:
            # fade out
            self.opacity -= 25
            self.song.arrows_area.image.blit(
                self.image, self.rect  # , special_flags=pygame.BLEND_RGB_ADD
            )
        if self.playing and self.song.song_frame < self.time + self.duration:
            dist = (self.song.song_frame - self.time) / min(40, self.duration)
            if dist > 1:
                dist = 0
            self.image = pygame.transform.scale(
                self.image_copy,
                (
                    int(
                        self.song.arrows_area.arrow_size[0]
                        + self.ENLARGE_SIZE * math.sin(math.pi * dist)
                    ),
                    int(
                        self.song.arrows_area.arrow_size[1]
                        + self.ENLARGE_SIZE * math.sin(math.pi * dist)
                    ),
                ),
            )
            if self.grow_center is None:
                self.grow_center = self.rect.center
            self.rect = self.image.get_rect(center=self.grow_center)
        else:
            self.grow_center = None

    def play(self):
        self.playing = True
        self.song.arrows_area.controls.glow(self.group)
