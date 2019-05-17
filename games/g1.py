import pygame
from pygame.locals import *
import sys

white = 255, 255, 255
blue = 0, 0, 200

pygame.init()

screen = pygame.display.set_mode((600, 500))
myfont = pygame.font.Font(None, 60)
text_image = myfont.render('hello pygame', True, white)

while True:
    for event in pygame.event.get():
        if event.type in (QUIT, KEYDOWN):
            sys.exit()
    screen.fill(blue)
    screen.blit(text_image, (100, 100))
    pygame.display.update()



