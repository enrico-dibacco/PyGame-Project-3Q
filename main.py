import pygame as pg
from sys import exit
from player import Player
from enemy import Enemy
import random
import numpy as np

pg.mixer.pre_init(frequency=44100, size=-16, channels=2)  # stereo-safe
pg.init()

screen = pg.display.set_mode((1920, 1080))
clock = pg.time.Clock()

player = Player((960, 540))
all_sprites = pg.sprite.Group(player)
enemy_group = pg.sprite.Group()

spawn_timer = 0
SPAWN_INTERVAL = 1500

original_death_sound = pg.mixer.Sound("sfx/death.wav")

def play_random_pitch(sound, pitch_range=(0.95, 1.05)):
    pitch = np.random.uniform(*pitch_range)
    arr = pg.sndarray.array(sound)

    if len(arr.shape) > 1 and arr.shape[1] == 2:
        arr = arr.mean(axis=1).astype(arr.dtype)

    orig_len = len(arr)
    new_len = int(orig_len / pitch)
    arr = np.interp(np.linspace(0, orig_len, new_len), np.arange(orig_len), arr).astype(arr.dtype)

    stereo_arr = np.column_stack((arr, arr))  # duplicate mono into stereo
    sound_variant = pg.sndarray.make_sound(stereo_arr)
    sound_variant.play()

while True:
    dt = clock.tick(60)
    spawn_timer += dt

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            player.swing_timer = 6

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
                play_random_pitch(original_death_sound)

    if player.swing_timer > 0:
        for enemy in enemy_group:
            if enemy.state == "approaching" and enemy.is_special:
                if player.shield_collides(enemy.rect):
                    enemy.knockback()

    for enemy in enemy_group:
        if enemy.state == "vulnerable":
            if player.shield_collides(enemy.rect):
                enemy.kill()
                play_random_pitch(original_death_sound)

    screen.fill((255, 255, 255))
    player.draw(screen)
    enemy_group.draw(screen)
    pg.display.flip()
