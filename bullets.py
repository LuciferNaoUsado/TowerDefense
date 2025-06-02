# bullets.py

import pygame
import math
from game_state import game_state
from config import SCALE, BULLET_BASE_SIZE

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_screen, target, damage=1, speed=5, image_path=None):
        """
        pos_screen: (x, y) em coordenadas de tela (já escaladas) de onde dispara.
        target: instância de Enemy (com rect.center em tela).
        """
        super().__init__()
        self.pos = list(pos_screen)
        self.target = target
        self.damage = damage
        self.speed = speed * SCALE  # velocidade proporcional ao SCALE

        if image_path:
            img = pygame.image.load(image_path).convert_alpha()
            # Redimensiona para BULLET_BASE_SIZE × BULLET_BASE_SIZE (na base)
            img = pygame.transform.scale(img, (BULLET_BASE_SIZE, BULLET_BASE_SIZE))
            # Agora escalar para (BULLET_BASE_SIZE × SCALE)
            size = max(int(BULLET_BASE_SIZE * SCALE), 1)
            self.image = pygame.transform.scale(img, (size, size))
        else:
            # fallback: pequeno círculo amarelo
            radius = max(int(5 * SCALE), 1)
            self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (240, 240, 80), (radius, radius), radius)

        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        # Se o alvo já morreu, remove a bala
        if not self.target.alive():
            self.kill()
            return

        tx, ty = self.target.rect.center
        dx = tx - self.pos[0]
        dy = ty - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist < self.speed or dist == 0:
            self.target.take_damage(self.damage)
            self.kill()
        else:
            self.pos[0] += dx / dist * self.speed
            self.pos[1] += dy / dist * self.speed
            self.rect.center = self.pos

class BasicBullet(Bullet):
    def __init__(self, pos_screen, target):
        super().__init__(
            pos_screen,
            target,
            damage=1,
            speed=5,
            image_path="assets/bullet_basic.png"
        )

class HeavyBullet(Bullet):
    def __init__(self, pos_screen, target):
        super().__init__(
            pos_screen,
            target,
            damage=3,
            speed=3,
            image_path="assets/bullet_heavy.png"
        )
