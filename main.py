
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
from potion import Potion

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
screen_width, screen_height = screen.get_size()
clock = pg.time.Clock()

score = Score("fonts/munro.ttf", font_size=80, color=(0,0,0), position=(1500,150))
background = pg.transform.scale(pg.image.load("envrioment/rockfloor.png").convert(), (1920,1080))
healthb = HealthBar(220,150,200,20,100)
player = Player((960,540))
all_sprites = pg.sprite.Group(player)
enemy_group = pg.sprite.Group()
fireballs = pg.sprite.Group()
particles = pg.sprite.Group()
potions = pg.sprite.Group()
enemy_projectiles = pg.sprite.Group()
player.enemy_projectiles = enemy_projectiles

spawn_timer = 0
potion_timer = 0
wave_timer = 0
SPAWN_INTERVAL = 1500
POTION_INTERVAL = 10000
WAVE_DURATION = 60000
FIREBALL_COOLDOWN = 1000
last_fireball_time = 0

current_wave = 1
enemies_per_wave = 1
enemy_speed_multiplier = 1.0
font_wave = pg.font.Font("fonts/munro.ttf", 80)
show_wave_announcement = True
wave_announcement_time = 0
WAVE_ANNOUNCE_DURATION = 15000

fireball_images = [
    pg.image.load("fireballanimation/fireball1.png").convert_alpha(),
    pg.image.load("fireballanimation/fireball2.png").convert_alpha()
]

original_death_sound = pg.mixer.Sound("sfx/death.wav")
knockback_sound = pg.mixer.Sound("sfx/knockback.wav")
blipSelect_sound = pg.mixer.Sound("sfx/blipSelect.wav")
powerup_sound = pg.mixer.Sound("sfx/powerup.wav")
hithurt_sound = pg.mixer.Sound("sfx/hithurt.wav")

shake_timer = 0
shake_magnitude = 8
maxmode = False
show_settings = False
music_volume = 0.1
sfx_volume = 0.5
font = pg.font.Font("fonts/munro.ttf", 36)

pg.mixer.music.load("music/bossphaseone.wav")
pg.mixer.music.set_volume(music_volume)
pg.mixer.music.play(-1)

MENU = "menu"
PLAYING = "playing"
GAMEOVER = "gameover"
game_state = MENU

def draw_main_menu():
    screen.fill((30,30,30))
    title = font_wave.render("DUNGEON SLASHER", True, (255,255,255))
    start = font.render("Press [SPACE] to Start", True, (200,200,200))
    screen.blit(title, title.get_rect(center=(960,300)))
    screen.blit(start, start.get_rect(center=(960,500)))
    pg.display.flip()

def draw_gameover():
    screen.fill((0,0,0))
    over = font_wave.render("GAME OVER", True, (255,0,0))
    retry = font.render("Press [R] to Restart or [ESC] to Quit", True, (255,255,255))
    screen.blit(over, over.get_rect(center=(960,300)))
    screen.blit(retry, retry.get_rect(center=(960,500)))
    pg.display.flip()

def play_random_pitch(sound, pitch_range=(0.95,1.05)):
    pitch = np.random.uniform(*pitch_range)
    arr = pg.sndarray.array(sound)
    if arr.ndim > 1 and arr.shape[1] == 2:
        arr = arr.mean(axis=1).astype(arr.dtype)
    orig_len = len(arr)
    new_len = int(orig_len/pitch)
    arr = np.interp(np.linspace(0,orig_len,new_len), np.arange(orig_len), arr).astype(arr.dtype)
    stereo = np.column_stack((arr,arr))
    snd_variant = pg.sndarray.make_sound(stereo)
    snd_variant.set_volume(sfx_volume)
    snd_variant.play()

def launch_fireballs(origin):
    for i in range(12):
        angle = math.radians(i*30)
        fb = Fireball(origin, angle, fireball_images)
        fireballs.add(fb)

def spawn_particles(pos, count=10):
    for _ in range(count):
        particles.add(Particle(pos))

def spawn_potion():
    kind = random.choice(["speed","multiplier","nuke"])
    potions.add(Potion(kind))

while True:
    dt = clock.tick(60)

    if game_state == MENU:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                player.health = 100
                healthb.current_health = 100
                score.reset()
                enemy_group.empty(); fireballs.empty(); potions.empty()
                spawn_timer = potion_timer = wave_timer = 0
                current_wave = 1; enemies_per_wave = 1; enemy_speed_multiplier = 1.0
                show_wave_announcement = True
                game_state = PLAYING
        draw_main_menu()
        continue

    if game_state == GAMEOVER:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    player.health = 100
                    healthb.current_health = 100
                    score.reset()
                    enemy_group.empty(); fireballs.empty(); potions.empty()
                    spawn_timer = potion_timer = wave_timer = 0
                    current_wave = 1
                    enemies_per_wave = 1
                    enemy_speed_multiplier = 1.0
                    show_wave_announcement = True
                    pg.mixer.music.stop()
                    pg.mixer.music.load("music/bossphaseone.wav")
                    pg.mixer.music.set_volume(music_volume)
                    pg.mixer.music.play(-1)
                    player.speed = 5
                    maxmode = False
                    game_state = PLAYING
                    healthb.current_health = 100
                    score.reset()
                    enemy_group.empty(); fireballs.empty(); potions.empty()
                    spawn_timer = potion_timer = wave_timer = 0
                    current_wave = 1; enemies_per_wave = 1; enemy_speed_multiplier = 1.0
                    show_wave_announcement = True
                    game_state = PLAYING
                elif event.key == pg.K_ESCAPE:
                    pg.quit(); exit()
        draw_gameover()
        continue

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit(); exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit(); exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_h:
            show_settings = not show_settings
        if not show_settings:
            if event.type == pg.KEYDOWN and event.key == pg.K_PLUS:
                SPAWN_INTERVAL = max(200, SPAWN_INTERVAL-100)
            if event.type == pg.KEYDOWN and event.key == pg.K_m:
                pg.mixer.music.stop()
                pg.mixer.music.load("music/max.wav")
                pg.mixer.music.set_volume(1)
                pg.mixer.music.play(-1)
                player.speed *= 5; maxmode = True
                play_random_pitch(blipSelect_sound)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                player.swing_timer = 6
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                now = pg.time.get_ticks()
                if now - last_fireball_time >= FIREBALL_COOLDOWN:
                    launch_fireballs(player.rect.center)
                    last_fireball_time = now
        if show_settings and event.type == pg.KEYDOWN:
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
        spawn_timer  += dt
        potion_timer += dt
        wave_timer   += dt

        if wave_timer >= WAVE_DURATION:
            current_wave += 1
            wave_timer = 0
            enemies_per_wave += 1
            enemy_speed_multiplier += 0.1
            show_wave_announcement = True
            wave_announcement_time = pg.time.get_ticks()

        keys = pg.key.get_pressed()
        all_sprites.update(keys)

        player.rect.left   = max(player.rect.left,   10)
        player.rect.right  = min(player.rect.right,  screen_width-10)
        player.rect.top    = max(player.rect.top,    10)
        player.rect.bottom = min(player.rect.bottom, screen_height-10)

        fireballs.update()
        enemy_group.update()
        particles.update()
        potions.update()
        enemy_projectiles.update()

        if spawn_timer >= SPAWN_INTERVAL:
            for _ in range(enemies_per_wave):
                special = random.random() < 0.3
                sx = random.choice([-50, screen_width+50])
                sy = random.randint(0, screen_height-1)
                e = Enemy(sx, sy, player, special)
                e.speed *= enemy_speed_multiplier
                enemy_group.add(e)
            spawn_timer = 0

        if potion_timer >= POTION_INTERVAL:
            spawn_potion()
            potion_timer = 0
        for fb in fireballs:
            for e in list(enemy_group):
                if fb.rect.colliderect(e.rect):
                    spawn_particles(e.rect.center)
                    play_random_pitch(original_death_sound)
                    score.add(50 * getattr(score, "multiplier", 1))
                    e.kill()
                    fb.kill()
                    shake_timer = 8

        if player.swing_timer > 0:
            for e in list(enemy_group):
                if e.state == "approaching" and player.shield_collides(e.rect):
                    if e.is_special:
                        score.add(50 * getattr(score, "multiplier", 1))
                        e.knockback()
                        play_random_pitch(knockback_sound)
                    else:
                        spawn_particles(e.rect.center)
                        play_random_pitch(original_death_sound)
                        score.add(100 * getattr(score, "multiplier", 1))
                        e.kill()
                        shake_timer = 8

        for e in list(enemy_group):
            if e.state == "vulnerable" and player.shield_collides(e.rect):
                spawn_particles(e.rect.center)
                play_random_pitch(original_death_sound)
                score.add(100 * getattr(score, "multiplier", 1))
                e.kill()
                shake_timer = 8
            elif player.player_collides(e.rect):
                player.health -= 10
                healthb.current_health = player.health
                spawn_particles(e.rect.center)
                play_random_pitch(original_death_sound)
                e.kill()
                shake_timer = 8

        for proj in list(enemy_projectiles):
            if player.player_collides(proj.rect):
                player.health -= 10
                healthb.current_health = player.health
                proj.kill()
                shake_timer = 8

        for pot in list(potions):
            if player.rect.colliderect(pot.rect):
                pot.apply_effect(player, score, enemy_group)
                pot.kill()
                play_random_pitch(powerup_sound)

        now = pg.time.get_ticks()
        if hasattr(player, "speed_timer") and now - player.speed_timer > 30000:
            player.speed = 5
            del player.speed_timer
        if hasattr(score, "multiplier_timer") and now - score.multiplier_timer > 30000:
            del score.multiplier
            del score.multiplier_timer

    if shake_timer > 0:
        offset = (random.randint(-shake_magnitude,shake_magnitude),
                  random.randint(-shake_magnitude,shake_magnitude))
        shake_timer -= 1
    else:
        offset = (0,0)

    screen.blit(background, offset)
    player.draw(screen, offset)
    fireballs.draw(screen)
    enemy_group.draw(screen)
    particles.draw(screen)
    enemy_projectiles.draw(screen)
    potions.draw(screen)
    healthb.draw(screen)
    score.draw(screen)

    if show_wave_announcement:
        elapsed = pg.time.get_ticks() - wave_announcement_time
        if elapsed < WAVE_ANNOUNCE_DURATION:
            alpha = int(255 * (1 - elapsed / WAVE_ANNOUNCE_DURATION))
            txt = font_wave.render(f"WAVE {current_wave}", True, (255,0,0))
            txt.set_alpha(alpha)
            screen.blit(txt, txt.get_rect(center=(960,200)))
        else:
            show_wave_announcement = False

    if show_settings:
        surf = pg.Surface((700,400))
        surf.fill((230,230,230))
        surf.set_alpha(240)
        screen.blit(surf, (610,300))
        mtxt = font.render(f"Music Volume: {int(music_volume*100)}%", True, (0,0,0))
        stxt = font.render(f"SFX Volume:   {int(sfx_volume*100)}%", True, (0,0,0))
        screen.blit(mtxt, (650,340))
        screen.blit(stxt, (650,380))
        pg.draw.rect(screen, (100,100,100), (650,375,200,10))
        pg.draw.rect(screen, (160,0,160),  (650,375,int(music_volume*200),10))
        pg.draw.rect(screen, (100,100,100), (650,415,200,10))
        pg.draw.rect(screen, (255,100,0),   (650,415,int(sfx_volume*200),10))
        ctl = font.render("CONTROLS:", True, (0,0,0))
        lines = ["WASD = move", "Mouse L = Shield Bash", "Q = Fireballs",
                 "H = Toggle Settings", "←/→ = Music vol", "↓/↑ = SFX vol"]
        screen.blit(ctl, (650,450))
        for i,line in enumerate(lines):
            screen.blit(font.render(line,True,(0,0,0)), (670,480+i*30))

    if player.health <= 0:
        game_state = GAMEOVER
        SPAWN_INTERVAL = 1500
        player.rect.center = (960, 540)

    pg.display.flip()
