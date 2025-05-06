import pygame as pg
from sys import exit
from player import Player
pg.init()
screen = pg.display.set_mode((1920,1080))
clock = pg.time.Clock()
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

    pg.display.update()
    clock.tick(60)
    