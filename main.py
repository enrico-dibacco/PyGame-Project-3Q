import pygame as pg
import math
import random
import numpy as np
from sys import exit
from player import Player
from enemy import Enemy
from score import Score
from healthbar import HealthBar
from fireball import Fireball
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

pg.mixer.pre_init(frequency=44100, size=-16, channels=2)
pg.init()

screen = pg.display.set_mode((1920, 1080))
score = Score("fonts/munro.ttf", font_size=80, color=(0, 0, 0), position=(1500, 150))
background = pg.transform.scale(pg.image.load("envrioment/rockfloor.png").convert(), (1920, 1080))
clock = pg.time.Clock()
healthb = HealthBar(300, 300, 200, 20, 100)
player = Player((960, 540))
all_sprites = pg.sprite.Group(player)
enemy_group = pg.sprite.Group()
fireballs = pg.sprite.Group()
particles = pg.sprite.Group()

spawn_timer = 0
SPAWN_INTERVAL = 1500
FIREBALL_COOLDOWN = 1000
last_fireball_time = 0

fireball_images = [
    pg.image.load("fireballanimation/fireball1.png").convert_alpha(),
    pg.image.load("fireballanimation/fireball2.png").convert_alpha()
]

original_death_sound = pg.mixer.Sound("sfx/death.wav")

shake_timer = 0
shake_magnitude = 8

def play_sound(soundname, volume=0.5, loop=False):
    sound = pg.mixer.Sound(f"{soundname}")
    sound.set_volume(volume)
    if loop:
        sound.play(-1)
    else:
        sound.play()

def play_random_pitch(sound, pitch_range=(0.95, 1.05)):
    pitch = np.random.uniform(*pitch_range)
    arr = pg.sndarray.array(sound)
    if len(arr.shape) > 1 and arr.shape[1] == 2:
        arr = arr.mean(axis=1).astype(arr.dtype)
    orig_len = len(arr)
    new_len = int(orig_len / pitch)
    arr = np.interp(np.linspace(0, orig_len, new_len), np.arange(orig_len), arr).astype(arr.dtype)
    stereo_arr = np.column_stack((arr, arr))
    sound_variant = pg.sndarray.make_sound(stereo_arr)
    sound_variant.play()

def launch_fireballs(origin):
    for i in range(12):
        angle = i * 30 * math.pi / 180
        fireball = Fireball(origin, angle, fireball_images)
        fireballs.add(fireball)

def spawn_particles(pos, count=10):
    for _ in range(count):
        particles.add(Particle(pos))

play_sound("music/bossphaseone.wav", 0.1, True)

while True:
    dt = clock.tick(60)
    spawn_timer += dt

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            player.swing_timer = 6
        if event.type == pg.KEYDOWN and event.key == pg.K_q:
            now = pg.time.get_ticks()
            if now - last_fireball_time >= FIREBALL_COOLDOWN:
                launch_fireballs(player.rect.center)
                last_fireball_time = now

    keys = pg.key.get_pressed()
    all_sprites.update(keys)
    fireballs.update()
    enemy_group.update()
    particles.update()

    if spawn_timer >= SPAWN_INTERVAL:
        special = random.random() < 0.3
        enemy = Enemy(1920, 1080, player, special)
        enemy_group.add(enemy)
        spawn_timer = 0

    for fireball in fireballs:
        for enemy in enemy_group:
            if fireball.rect.colliderect(enemy.rect):
                spawn_particles(enemy.rect.center)
                enemy.kill()
                score.add(50)
                fireball.kill()
                play_random_pitch(original_death_sound)
                shake_timer = 8

    for enemy in enemy_group:
        if enemy.state == "approaching" and not enemy.is_special:
            if player.shield_collides(enemy.rect):
                spawn_particles(enemy.rect.center)
                enemy.kill()
                score.add(100)
                play_random_pitch(original_death_sound)
                shake_timer = 8

    if player.swing_timer > 0:
        for enemy in enemy_group:
            if enemy.state == "approaching" and enemy.is_special:
                if player.shield_collides(enemy.rect):
                    score.add(50)
                    enemy.knockback()

    for enemy in enemy_group:
        if enemy.state == "vulnerable" and player.shield_collides(enemy.rect):
            spawn_particles(enemy.rect.center)
            enemy.kill()
            score.add(100)
            play_random_pitch(original_death_sound)
            shake_timer = 8
        if player.player_collides(enemy.rect):
            player.health -= 10
            healthb.current_health = player.health
            spawn_particles(enemy.rect.center)
            enemy.kill()
            shake_timer = 8
            if player.health <= 0:
                print("Game Over")
                pg.quit()
                exit()

    if shake_timer > 0:
        shake_offset = (random.randint(-shake_magnitude, shake_magnitude), random.randint(-shake_magnitude, shake_magnitude))
        shake_timer -= 1
    else:
        shake_offset = (0, 0)

    screen.blit(background, shake_offset)
    player.draw(screen, shake_offset)
    fireballs.draw(screen)
    enemy_group.draw(screen)
    particles.draw(screen)
    healthb.draw(screen)
    score.draw(screen)
    pg.display.flip()
