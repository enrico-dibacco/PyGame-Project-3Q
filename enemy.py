import pygame as pg
import random
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, player, is_special=False):
        super().__init__()

        self.player = player
        self.is_special = is_special
        self.state = "approaching"
        self.speed = 2
        self.knockback_distance = 100

        if self.is_special:
            self.frames = [
                pg.image.load("mageanimation/mage1.png").convert_alpha(),
                pg.image.load("mageanimation/mage2.png").convert_alpha()
            ]
            self.frames = [pg.transform.scale(f, (100, 100)) for f in self.frames]
        else:
            self.frames = [
                pg.image.load("batanimation/enemy1.png").convert_alpha(),
                pg.image.load("batanimation/enemy2.png").convert_alpha(),
                pg.image.load("batanimation/enemy3.png").convert_alpha()
            ]
            self.frames = [pg.transform.scale(f, (60, 60)) for f in self.frames]

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  

        self.knockback_timer = 0
        self.anim_index = 0
        self.anim_direction = 1
        self.anim_timer = 0
        self.anim_speed = 10


    def update(self):
        self.animate()

        if self.state == "approaching":
            self.move_toward_player()
        elif self.state == "knocked":
            self.move_away_from_player()
            self.knockback_timer -= 1
            if self.knockback_timer <= 0:
                self.state = "vulnerable"
        elif self.state == "vulnerable":
            self.move_toward_player()

    def animate(self):
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index += self.anim_direction

            if self.anim_index >= len(self.frames) - 1:
                self.anim_direction = -1
            elif self.anim_index <= 0:
                self.anim_direction = 1

            self.image = self.frames[self.anim_index]

    def move_toward_player(self):
        self.move_towards_point(self.player.rect.center, self.speed)

    def move_away_from_player(self):
        px, py = self.player.rect.center
        ex, ey = self.rect.center
        dx, dy = ex - px, ey - py
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
        self.rect.x += dx * self.speed * 2
        self.rect.y += dy * self.speed * 2

    def move_towards_point(self, point, speed):
        ex, ey = self.rect.center
        tx, ty = point
        dx, dy = tx - ex, ty - ey
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
        self.rect.x += dx * speed
        self.rect.y += dy * speed

    def knockback(self):
        if self.is_special and self.state == "approaching":
            self.state = "knocked"
            self.knockback_timer = 30
