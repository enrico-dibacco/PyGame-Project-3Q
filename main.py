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
    keys = pg.key.get_pressed() #i get the keys pressed to move the player
    all_sprites.update(keys)
    #here i draw the background and the player
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)    


    pg.display.update()
    clock.tick(60)
    