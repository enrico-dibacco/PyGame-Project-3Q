import pygame as pg
from sys import exit

screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
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
    