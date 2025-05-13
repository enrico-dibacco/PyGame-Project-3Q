import pygame as pg
from sys import exit
from player import Player
from enemy import Enemy
import random

pg.init()
screen = pg.display.set_mode((1920, 1080))
clock = pg.time.Clock()

player = Player((960, 540))
all_sprites = pg.sprite.Group(player)
enemy_group = pg.sprite.Group()

spawn_timer = 0
SPAWN_INTERVAL = 1500

while True:
    dt = clock.tick(60)
    spawn_timer += dt

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            player.swing_timer = 6  # ~100ms swing buffer

    keys = pg.key.get_pressed()
    all_sprites.update(keys)
    enemy_group.update()

    if spawn_timer >= SPAWN_INTERVAL:
        special = random.random() < 0.3
        enemy = Enemy(1920, 1080, player, special)
        enemy_group.add(enemy)
        spawn_timer = 0

    for enemy in enemy_group:
        if enemy.state == "approaching" and not enemy.is_special:
            if player.shield_collides(enemy.rect):
                enemy.kill()

    if player.swing_timer > 0:
        for enemy in enemy_group:
            if enemy.state == "approaching" and enemy.is_special:
                if player.shield_collides(enemy.rect):
                    enemy.knockback()

    for enemy in enemy_group:
        if enemy.state == "vulnerable":
            if player.shield_collides(enemy.rect):
                enemy.kill()

    for enemy in enemy_group:
        if player.player_collide(enemy.rect):
            player.healthManager(10)
            
            enemy.kill()
           
                

    screen.fill((255, 255, 255))
    player.draw(screen)
    enemy_group.draw(screen)
    pg.display.flip()

