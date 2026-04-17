import pygame

class Ball:
    def __init__(self, x, y, radius=25, color=(255,0,0), step=20):
        self.x, self.y = x, y
        self.radius, self.color, self.step = radius, color, step
    
    def move(self, dx, dy, w, h):
        nx, ny = self.x + dx, self.y + dy
        if self.radius <= nx <= w - self.radius: self.x = nx
        if self.radius <= ny <= h - self.radius: self.y = ny
    
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)