import pygame, sys
from ball import Ball

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Moving Ball")
ball = Ball(W//2, H//2)
clock = pygame.time.Clock()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key in (pygame.K_q, pygame.K_ESCAPE)):
            pygame.quit(); sys.exit()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]: ball.move(0, -ball.step, W, H)
    if keys[pygame.K_DOWN]: ball.move(0, ball.step, W, H)
    if keys[pygame.K_LEFT]: ball.move(-ball.step, 0, W, H)
    if keys[pygame.K_RIGHT]: ball.move(ball.step, 0, W, H)
    
    screen.fill((255,255,255))
    ball.draw(screen)
    pygame.display.flip()
    clock.tick(60)