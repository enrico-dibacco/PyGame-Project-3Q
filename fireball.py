import pygame
import math

class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos, angle, images):
        super().__init__()
        self.images = images
        self.current_frame = 0
        self.frame_timer = 0
        self.animation_interval = 100

        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=pos)

        self.speed = 10
        self.angle = angle
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * self.speed

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        self.frame_timer += 1
        if self.frame_timer >= self.animation_interval:
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
            self.frame_timer = 0

        # Remove if out of screen bounds
        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()
