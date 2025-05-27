import pygame as pg
import random
import math

class Particle(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((6, 6), pg.SRCALPHA)
        self.image.fill((255, 50, 50))
        self.rect = self.image.get_rect(center=pos)
        self.velocity = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.life = 30

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.life -= 1
        if self.life <= 0:
            self.kill()
class Potion(pg.sprite.Sprite):
    def __init__(self, potion_type):
        super().__init__()
        self.potion_type = potion_type

        self.image = pg.image.load(f"potions/{potion_type}.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(random.randint(100, 1800), random.randint(100, 900)))
        self.base_y = self.rect.centery  # bobbing base position

        self.spawn_time = pg.time.get_ticks()
        self.flash_timer = 0
        self.flashing = False

    def update(self):
        now = pg.time.get_ticks()
        age = now - self.spawn_time

        
        self.rect.centery = self.base_y + int(math.sin(now / 200) * 5)

        if age > 30000:
            self.flashing = True
            if (now // 250) % 2 == 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(50)

            if age > 35000:
                self.kill()

    def apply_effect(self, player, score, enemy_group):
        now = pg.time.get_ticks()

        if self.potion_type == "speed":
            player.speed *= 1.5
            player.speed_timer = now

        elif self.potion_type == "multiplier":
            score.multiplier = 3
            score.multiplier_timer = now

        elif self.potion_type == "nuke":
            for enemy in enemy_group:
                enemy.kill()
                
            if hasattr(player, "shake_timer"):
                player.shake_timer = 8  
