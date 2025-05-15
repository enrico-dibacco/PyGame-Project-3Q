import pygame as pg
import random
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, screen_width, screen_height, player, is_special=False):
        super().__init__()

        self.player = player
        self.is_special = is_special
        self.state = "approaching"
        self.speed = 2
        self.knockback_distance = 100

        if self.is_special:
            # Just a plain blue square
            surface = pg.Surface((30, 30))
            surface.fill((0, 0, 255))
            self.frames = [surface]
        else:
            # Load animated frames from image files
            self.frames = [
                pg.image.load("batanimation/enemy1.png").convert_alpha(),
                pg.image.load("batanimation/enemy2.png").convert_alpha(),
                pg.image.load("batanimation/enemy3.png").convert_alpha()
            ]
            self.frames = [pg.transform.scale(f, (60, 60)) for f in self.frames]

        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        # Spawn enemy randomly on screen edge
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

        # Animation (used only for non-special enemies)
        self.anim_index = 0
        self.anim_direction = 1
        self.anim_timer = 0
        self.anim_speed = 10

    def update(self):
        if not self.is_special:
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

            if self.anim_index == 2:
                self.anim_direction = -1
            elif self.anim_index == 0:
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
