import pygame

class HealthBar:
    def __init__(self, x, y, w, h, max_health):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_health = max_health
        self.current_health = max_health

    def draw(self, screen):
        ratio = self.current_health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.w * ratio, self.h))
        