import pygame as pg
from sys import exit
from player import Player
pg.init()
screen = pg.display.set_mode((1920,1080))
clock = pg.time.Clock()
player = Player((960, 540))
all_sprites = pg.sprite.Group() #i use the group to manage all the sprites and i want to make collisions easier to handle
all_sprites.add(player)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

    keys = pg.key.get_pressed()
    all_sprites.update(keys)

    #draw everything
    screen.fill((0, 0, 0))       #clear screen
    player.draw(screen)         #draw player + shield

    pg.display.flip()           #update full display
    clock.tick(60)              #cap to 60 FPS
    