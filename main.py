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
from potion import Potion  # <-- pozioni!

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
healthb = HealthBar(220, 150, 200, 20, 100)
player = Player((960, 540))
all_sprites = pg.sprite.Group(player)
enemy_group = pg.sprite.Group()
fireballs = pg.sprite.Group()
particles = pg.sprite.Group()
potions = pg.sprite.Group()

spawn_timer = 0
potion_timer = 0
SPAWN_INTERVAL = 1500
POTION_INTERVAL = 10000
FIREBALL_COOLDOWN = 1000
last_fireball_time = 0

fireball_images = [
    pg.image.load("fireballanimation/fireball1.png").convert_alpha(),
    pg.image.load("fireballanimation/fireball2.png").convert_alpha()
]

original_death_sound = pg.mixer.Sound("sfx/death.wav")
knockback_sound = pg.mixer.Sound("sfx/knockback.wav")
blipSelect_sound = pg.mixer.Sound("sfx/blipSelect.wav")
powerup_sound = pg.mixer.Sound("sfx/powerup.wav")

shake_timer = 0
shake_magnitude = 8

enemy_projectiles = pg.sprite.Group()
player.enemy_projectiles = enemy_projectiles

show_settings = False
music_volume = 0.1
sfx_volume = 0.5
font = pg.font.Font("fonts/munro.ttf", 36)

pg.mixer.music.load("music/bossphaseone.wav")
pg.mixer.music.set_volume(music_volume)
pg.mixer.music.play(-1)

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
    sound_variant.set_volume(sfx_volume)
    sound_variant.play()

def launch_fireballs(origin):
    for i in range(12):
        angle = i * 30 * math.pi / 180
        fireball = Fireball(origin, angle, fireball_images)
        fireballs.add(fireball)

def spawn_particles(pos, count=10):
    for _ in range(count):
        particles.add(Particle(pos))

def spawn_potion():
    kind = random.choice(["speed", "multiplier", "nuke"])
    potions.add(Potion(kind))

while True:
    dt = clock.tick(60)
    spawn_timer += dt
    potion_timer += dt

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and (event.key == pg.K_ESCAPE or event.key == pg.K_TAB)):
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_h:
                show_settings = not show_settings
            elif show_settings:
                if event.key == pg.K_LEFT:
                    music_volume = max(0.0, music_volume - 0.05)
                    pg.mixer.music.set_volume(music_volume)
                    play_random_pitch(blipSelect_sound)
                elif event.key == pg.K_RIGHT:
                    music_volume = min(1.0, music_volume + 0.05)
                    pg.mixer.music.set_volume(music_volume)
                    play_random_pitch(blipSelect_sound)
                elif event.key == pg.K_DOWN:
                    sfx_volume = max(0.0, sfx_volume - 0.05)
                    play_random_pitch(blipSelect_sound)
                elif event.key == pg.K_UP:
                    sfx_volume = min(1.0, sfx_volume + 0.05)
                    play_random_pitch(blipSelect_sound)
        if not show_settings:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                player.swing_timer = 6
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                now = pg.time.get_ticks()
                if now - last_fireball_time >= FIREBALL_COOLDOWN:
                    launch_fireballs(player.rect.center)
                    last_fireball_time = now

    if not show_settings:
        keys = pg.key.get_pressed()
        all_sprites.update(keys)
        fireballs.update()
        enemy_group.update()
        particles.update()
        potions.update()
        enemy_projectiles.update()

        if spawn_timer >= SPAWN_INTERVAL:
            special = random.random() < 0.3
            enemy = Enemy(1920, 1080, player, special)
            enemy_group.add(enemy)
            spawn_timer = 0

        if potion_timer >= POTION_INTERVAL:
            spawn_potion()
            potion_timer = 0

        for fireball in fireballs:
            for enemy in enemy_group:
                if fireball.rect.colliderect(enemy.rect):
                    spawn_particles(enemy.rect.center)
                    enemy.kill()
                    score.add(50 if not hasattr(score, 'multiplier') else 50 * score.multiplier)
                    fireball.kill()
                    play_random_pitch(original_death_sound)
                    shake_timer = 8

        for enemy in enemy_group:
            if enemy.state == "approaching" and not enemy.is_special:
                if player.shield_collides(enemy.rect):
                    spawn_particles(enemy.rect.center)
                    enemy.kill()
                    score.add(100 if not hasattr(score, 'multiplier') else 100 * score.multiplier)
                    play_random_pitch(original_death_sound)
                    shake_timer = 8

        if player.swing_timer > 0:
            for enemy in enemy_group:
                if enemy.state == "approaching" and enemy.is_special:
                    if player.shield_collides(enemy.rect):
                        score.add(50 if not hasattr(score, 'multiplier') else 50 * score.multiplier)
                        enemy.knockback()
                        play_random_pitch(knockback_sound)

        for enemy in enemy_group:
            if enemy.state == "vulnerable" and player.shield_collides(enemy.rect):
                spawn_particles(enemy.rect.center)
                enemy.kill()
                score.add(100 if not hasattr(score, 'multiplier') else 100 * score.multiplier)
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

        for fb in enemy_projectiles:
            if player.player_collides(fb.rect):
                player.health -= 10
                healthb.current_health = player.health
                fb.kill()
                shake_timer = 8
                if player.health <= 0:
                    print("Game Over")
                    pg.quit()
                    exit()

        for potion in potions:
            if player.rect.colliderect(potion.rect):
                potion.apply_effect(player, score, enemy_group)
                potion.kill()
                play_random_pitch(powerup_sound)


        now = pg.time.get_ticks()
        if hasattr(player, 'speed_timer') and now - player.speed_timer > 30000:
            player.speed = 5
            del player.speed_timer
        if hasattr(score, 'multiplier_timer') and now - score.multiplier_timer > 30000:
            del score.multiplier
            del score.multiplier_timer

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
    enemy_projectiles.draw(screen)
    potions.draw(screen)
    healthb.draw(screen)
    score.draw(screen)

    if show_settings:
        settings_surface = pg.Surface((700, 400))
        settings_surface.fill((230, 230, 230))
        settings_surface.set_alpha(240)
        screen.blit(settings_surface, (610, 300))

        music_text = font.render(f"Music Volume: {int(music_volume * 100)}%", True, (0, 0, 0))
        sfx_text = font.render(f"SFX Volume: {int(sfx_volume * 100)}%", True, (0, 0, 0))
        screen.blit(music_text, (650, 340))
        screen.blit(sfx_text, (650, 380))

        pg.draw.rect(screen, (100, 100, 100), (650, 375, 200, 10))
        pg.draw.rect(screen, (160, 0, 160), (650, 375, int(music_volume * 200), 10))
        pg.draw.rect(screen, (100, 100, 100), (650, 415, 200, 10))
        pg.draw.rect(screen, (255, 100, 0), (650, 415, int(sfx_volume * 200), 10))

        controls_text = font.render("CONTROLS:", True, (0, 0, 0))
        lines = [
            "WASD = move",
            "Mouse Left = Shield Bash",
            "Q = Fireballs",
            "H = Toggle Settings",
            "Left/Right Arrows = Adjust Music Volume",
            "Up/Down Arrows = Adjust SFX Volume"
        ]
        screen.blit(controls_text, (650, 450))
        for i, line in enumerate(lines):
            line_text = font.render(line, True, (0, 0, 0))
            screen.blit(line_text, (670, 480 + i * 30))

    pg.display.flip()
