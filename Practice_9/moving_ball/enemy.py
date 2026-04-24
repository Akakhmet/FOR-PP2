import pygame

class Enemy:
    def __init__(self, x, y, size=28, speed=2, direction='h', range_val=120):
        self.start_x, self.start_y = float(x), float(y)
        self.x, self.y = float(x), float(y)
        self.size = size
        self.speed = speed
        self.direction = direction
        self.range_val = range_val
        self.moving_positive = True
        self.rect = pygame.Rect(int(x), int(y), size, size)

    def update(self):
        if self.direction == 'h':
            if self.moving_positive:
                self.x += self.speed
                if self.x >= self.start_x + self.range_val:
                    self.moving_positive = False
            else:
                self.x -= self.speed
                if self.x <= self.start_x:
                    self.moving_positive = True
        else:
            if self.moving_positive:
                self.y += self.speed
                if self.y >= self.start_y + self.range_val:
                    self.moving_positive = False
            else:
                self.y -= self.speed
                if self.y <= self.start_y:
                    self.moving_positive = True
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surf):
        # Тело
        pygame.draw.rect(surf, (20, 20, 20), self.rect)
        pygame.draw.rect(surf, (200, 0, 0), self.rect, 2)
        # Глаза
        eye = self.size // 5
        pygame.draw.rect(surf, (255, 0, 0),
                         (self.x + 5, self.y + 7, eye, eye))
        pygame.draw.rect(surf, (255, 0, 0),
                         (self.x + self.size - 5 - eye, self.y + 7, eye, eye))
        # Рот
        pygame.draw.line(surf, (255, 0, 0),
                         (int(self.x + 6), int(self.y + self.size - 8)),
                         (int(self.x + self.size - 6), int(self.y + self.size - 8)), 2)