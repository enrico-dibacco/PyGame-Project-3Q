import pygame as pg
from sys import exit
from player import Player
pg.init()
screen = pg.display.set_mode((1920,1080))
clock = pg.time.Clock()

all_sprites = pg.sprite.Group()
all_sprites.add(Player)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

    #here i draw the background and the player
    screen.fill((0, 0, 0))
        


    pg.display.update()
    clock.tick(60)
    