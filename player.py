import pygame
import math
import random
from enemy import Enemy

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        player_scale = 3
        sword_scale = 0.1

        walk1 = pygame.image.load("assets/walk1.png").convert_alpha()
        walk2 = pygame.image.load("assets/walk2.png").convert_alpha()
        walk1 = pygame.transform.scale(walk1, (int(walk1.get_width() * player_scale), int(walk1.get_height() * player_scale)))
        walk2 = pygame.transform.scale(walk2, (int(walk2.get_width() * player_scale), int(walk2.get_height() * player_scale)))
        self.walk_images_left = [walk1, walk2]
        self.walk_images_right = [pygame.transform.flip(img, True, False) for img in self.walk_images_left]

        idle = pygame.image.load("assets/idle.png").convert_alpha()
        idle = pygame.transform.scale(idle, (int(idle.get_width() * player_scale), int(idle.get_height() * player_scale)))
        self.idle_image_left = idle
        self.idle_image_right = pygame.transform.flip(idle, True, False)

        self.image = self.idle_image_left
        self.rect = self.image.get_rect(center=pos)

        self.speed = 5
        self.direction = "left"
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_interval = 200

        shield = pygame.image.load("assets/shield.png").convert_alpha()
        shield = pygame.transform.scale(shield, (int(shield.get_width() * sword_scale), int(shield.get_height() * sword_scale)))
        self.shield_base_image = shield
        self.shield_image = shield
        self.shield_radius = 80
        self.shield_angle = 0

        self.swing_timer = 0
        self.health = 100
    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
            self.direction = "left"
        if keys[pygame.K_d]:
            dx += self.speed
            self.direction = "right"

        self.rect.x += dx
        self.rect.y += dy

        moving = dx != 0 or dy != 0

        if moving:
            now = pygame.time.get_ticks()
            if now - self.last_update_time > self.animation_interval:
                self.current_frame = (self.current_frame + 1) % 2
                self.last_update_time = now

            if self.direction == "right":
                self.image = self.walk_images_right[self.current_frame]
            else:
                self.image = self.walk_images_left[self.current_frame]
        else:
            self.image = self.idle_image_right if self.direction == "right" else self.idle_image_left

        mx, my = pygame.mouse.get_pos()
        px, py = self.rect.center
        self.shield_angle = math.atan2(my - py, mx - px)

        if self.swing_timer > 0:
            self.swing_timer -= 1
            scale = 1.3
            scaled = pygame.transform.scale(
                self.shield_base_image,
                (
                    int(self.shield_base_image.get_width() * scale),
                    int(self.shield_base_image.get_height() * scale)
                )
            )
            self.shield_image = scaled
        else:
            self.shield_image = self.shield_base_image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        px, py = self.rect.center
        shield_x = px + self.shield_radius * math.cos(self.shield_angle)
        shield_y = py + self.shield_radius * math.sin(self.shield_angle)
        angle_deg = -math.degrees(self.shield_angle)-90
        rotated_shield = pygame.transform.rotate(self.shield_image, angle_deg)
        shield_rect = rotated_shield.get_rect(center=(shield_x, shield_y))
        surface.blit(rotated_shield, shield_rect)

    def shield_collides(self, other_rect):
        px, py = self.rect.center
        shield_x = px + self.shield_radius * math.cos(self.shield_angle)
        shield_y = py + self.shield_radius * math.sin(self.shield_angle)
        angle_deg = -math.degrees(self.shield_angle)-90
        rotated_shield = pygame.transform.rotate(self.shield_image, angle_deg)
        shield_rect = rotated_shield.get_rect(center=(shield_x, shield_y))
        return shield_rect.colliderect(other_rect)

    def player_collide(self, other_rect):
        return self.rect.colliderect(other_rect)

    def healthManager(self, dmg = 0, healing = 0):
        self.health -=  dmg
        self.health += healing
        if self.health <= 0:
            print("dead")
            #handle gameover here