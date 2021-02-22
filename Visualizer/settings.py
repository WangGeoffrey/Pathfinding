import pygame

pygame.init()
WIDTH = 612
ACROSS = 51
SIZE = WIDTH//ACROSS
SIDE_BAR = 100
WIN = pygame.display.set_mode((WIDTH+SIDE_BAR, WIDTH))
font = pygame.font.SysFont('Corbel', 15)
