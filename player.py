#i want to create a player that uses top down approach movement


import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
    def update(self, keys):
        dx = 0 #here im calculating the displacement in each of the 2 directions
        dy = 0
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed
        self.rect.x += dx
        self.rect.y += dy
        