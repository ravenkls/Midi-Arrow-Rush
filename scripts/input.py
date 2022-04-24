import sys

import pygame
from pygame.locals import *


class InputManager:
    def __init__(self, game):
        self.game = game
        self.arrows = []

    def process_inputs(self):
        for event in pygame.event.get():

            # Quit
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif self.game.screen == "game":
                self.process_game_inputs(event)
            elif self.game.screen == "menu":
                self.process_menu_inputs(event)
            elif self.game.screen == "list":
                self.process_list_inputs(event)

    def process_menu_inputs(self, event):
        if event.type == KEYDOWN:
            pygame.mixer.Sound.play(self.game.select)
            self.game.screen = "list"

    def process_list_inputs(self, event):
        if event.type == KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                self.game.level_list.move_up()
                pygame.mixer.Sound.play(self.game.click)
            elif event.key == K_s or event.key == K_DOWN:
                self.game.level_list.move_down()
                pygame.mixer.Sound.play(self.game.click)
            elif event.key == K_RETURN:
                self.game.level_list.select()
                pygame.mixer.Sound.play(self.game.select)
            elif event.key == K_ESCAPE:
                self.game.level_list.back()
                pygame.mixer.Sound.play(self.game.click)

    def process_game_inputs(self, event):
        if event.type == KEYDOWN:
            self.arrows = self.game.arrows_area.song.get_playable_arrows()
            if not self.arrows:
                self.game.score.value -= 100
            if event.key == K_ESCAPE:
                self.game.screen = "list"
                self.game.arrows_area.reset()
                pygame.mixer.Sound.play(self.game.click)
            elif event.key == K_a or event.key == K_LEFT:
                if self.arrows:
                    self.play_arrow_for_group(0)
                    self.game.score.value += 25
                self.game.arrows_area.controls.glow(0)
            elif event.key == K_w or event.key == K_UP:
                if self.arrows:
                    self.play_arrow_for_group(1)
                    self.game.score.value += 25

                self.game.arrows_area.controls.glow(1)
            elif event.key == K_s or event.key == K_DOWN:
                if self.arrows:
                    self.play_arrow_for_group(2)
                    self.game.score.value += 25
                self.game.arrows_area.controls.glow(2)
            elif event.key == K_d or event.key == K_RIGHT:
                if self.arrows:
                    self.play_arrow_for_group(3)
                    self.game.score.value += 25
                self.game.arrows_area.controls.glow(3)
        elif event.type == KEYUP:
            if event.key == K_a or event.key == K_LEFT:
                self.game.arrows_area.controls.stop_glow(0)
            elif event.key == K_w or event.key == K_UP:
                self.game.arrows_area.controls.stop_glow(1)
            elif event.key == K_s or event.key == K_DOWN:
                self.game.arrows_area.controls.stop_glow(2)
            elif event.key == K_d or event.key == K_RIGHT:
                self.game.arrows_area.controls.stop_glow(3)

    def play_arrow_for_group(self, n):
        played = False
        for a in self.arrows:
            if a.group == n:
                a.play()
                self.game.score.streak += 1
                played = True
                break
        if not played:
            self.game.score.streak = 0
        return played
