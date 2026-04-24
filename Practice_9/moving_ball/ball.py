import pygame

class Ball:
    def __init__(self, x, y, radius=15, color=(255, 50, 50), speed=4):
        self.start_x, self.start_y = x, y
        self.x, self.y = float(x), float(y)
        self.radius = radius
        self.color = color
        self.speed = speed
        self.vx, self.vy = 0.0, 0.0
        self.rect = pygame.Rect(0, 0, radius*2, radius*2)
        self.update_rect()

    def update_rect(self):
        self.rect.topleft = (int(self.x - self.radius), int(self.y - self.radius))

    def can_move(self, dx, dy, walls, screen_w, screen_h):
        new_rect = self.rect.move(int(dx), int(dy))
        for wall in walls:
            if new_rect.colliderect(wall):
                return False
        if new_rect.left < 0 or new_rect.right > screen_w:
            return False
        if new_rect.top < 0 or new_rect.bottom > screen_h:
            return False
        return True

    def update(self, walls, screen_w, screen_h):
        # Плавное движение с инерцией
        if self.can_move(self.vx, 0, walls, screen_w, screen_h):
            self.x += self.vx
        else:
            self.vx = 0
        if self.can_move(0, self.vy, walls, screen_w, screen_h):
            self.y += self.vy
        else:
            self.vy = 0
        # Трение
        self.vx *= 0.8
        self.vy *= 0.8
        self.update_rect()

    def accelerate(self, dx, dy):
        self.vx += dx
        self.vy += dy
        # Ограничение скорости
        max_spd = self.speed * 2
        self.vx = max(-max_spd, min(max_spd, self.vx))
        self.vy = max(-max_spd, min(max_spd, self.vy))

    def check_hazards(self, spikes, enemies):
        self.update_rect()
        for spike in spikes:
            if self.rect.colliderect(spike):
                return True
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                return True
        return False

    def check_goal(self, goal):
        self.update_rect()
        return self.rect.colliderect(goal)

    def reset(self):
        self.x, self.y = float(self.start_x), float(self.start_y)
        self.vx, self.vy = 0.0, 0.0
        self.update_rect()

    def draw(self, surf):
        glow = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 80),
                           (self.radius*2, self.radius*2), self.radius*2)
        surf.blit(glow, (self.x - self.radius*2, self.y - self.radius*2),
                  special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255,255,255), (int(self.x), int(self.y)), self.radius, 2)