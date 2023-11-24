import pygame
from sys import exit
import math
from settings import *

pygame.init()

#creating the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grand Theft Zombie")
clock = pygame.time.Clock()

#images
background = pygame.image.load("")

while True:
  keys = pygame.key.get_pressed()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      exit()
    