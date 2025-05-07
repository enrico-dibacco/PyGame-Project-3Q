import pygame as pg
import random
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, screen_width, screen_height, player, is_special=False): #i put the special enemy in the constructor so i can spawn it randomly
        super().__init__()

        self.player = player
        self.is_special = is_special
        self.state = "approaching"
        self.speed = 2
        self.knockback_distance = 100

        self.image = pg.Surface((30, 30))
        self.image.fill((0, 0, 255) if self.is_special else (255, 0, 0))
        self.rect = self.image.get_rect()

        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            self.rect.centerx = random.randint(0, screen_width)
            self.rect.top = 0
        elif edge == "bottom":
            self.rect.centerx = random.randint(0, screen_width)
            self.rect.bottom = screen_height
        elif edge == "left":
            self.rect.left = 0
            self.rect.centery = random.randint(0, screen_height)
        elif edge == "right":
            self.rect.right = screen_width
            self.rect.centery = random.randint(0, screen_height)

        self.knockback_timer = 0

    def update(self):
        if self.state == "approaching":
            self.move_toward_player()
        elif self.state == "knocked":
            self.move_away_from_player()
            self.knockback_timer -= 1
            if self.knockback_timer <= 0:
                self.state = "vulnerable"
        elif self.state == "vulnerable":
            self.move_toward_player()

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
