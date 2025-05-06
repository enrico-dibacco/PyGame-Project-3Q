#i want to create a player that uses top down approach movement
import math

import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5



        #shield logic

        self.shield_image = pygame.Surface((20, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.shield_image, (0, 255, 255), (0, 0, 20, 60))
        self.shield_radius = 80
        self.shield_angle = 0
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
       
        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.rect.center
        self.shield_angle = math.atan2(mouse_y - py, mouse_x - px)
    def draw(self, surface):
        
        surface.blit(self.image, self.rect)

        
        px, py = self.rect.center
        angle_deg = -math.degrees(self.shield_angle) + 90
        shield_x = px + self.shield_radius * math.cos(self.shield_angle)
        shield_y = py + self.shield_radius * math.sin(self.shield_angle)
        #here i compute the radius at which the shield will be drawn 
        
        rotated_shield = pygame.transform.rotate(self.shield_image, angle_deg)
        shield_rect = rotated_shield.get_rect(center=(shield_x, shield_y))
        surface.blit(rotated_shield, shield_rect)
        