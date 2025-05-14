import pygame
import math
import random
import time

class Score:
    def __init__(self, font_path: str, font_size: int = 24, color=(255, 255, 255), position=(10, 10)):
        self.score = 0
        self.color = color
        self.position = position  # (x, y)
        self.base_font_size = font_size
        self.font_path = font_path  # store path for animation resizing
        self.font = pygame.font.Font(font_path, font_size)

        self.anim_time = 0
        self.anim_duration = 0.4  # i believe this is in seconds
        self.last_update = time.time()

    def add(self, points: int):
        self.score += points
        self.anim_time = self.anim_duration  # trigger the animation

    def reset(self):
        self.score = 0

    def draw(self, surface):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        if self.anim_time > 0:
            self.anim_time -= dt
            progress = 1 - (self.anim_time / self.anim_duration)

            # scaling like luke's hose
            scale = 1 + 0.5 * math.sin(progress * math.pi)

            # shake shake effect (luke)
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
        else:
            scale = 1.0
            shake_x = 0
            shake_y = 0

        scaled_font_size = max(1, int(self.base_font_size * scale))
        temp_font = pygame.font.Font(self.font_path, scaled_font_size)

        score_text = f"{self.score}"
        text_surface = temp_font.render(score_text, True, self.color)
        text_rect = text_surface.get_rect(topleft=self.position)

        # apply that shaki shaki
        text_rect.x += shake_x
        text_rect.y += shake_y

        surface.blit(text_surface, text_rect)
