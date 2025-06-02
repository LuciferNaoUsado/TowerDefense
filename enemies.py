# enemies.py

import pygame
import math
import random
import paths
from config import ENEMY_REWARD, SCALE, ENEMY_BASE_SIZE
from game_state import game_state

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level_index=0):
        super().__init__()
        # Pega a lista de waypoints (em base 1536×1024) do level correspondente
        self.base_path = paths.PATHS[level_index]
        self.waypoint = 0
        # Posição base: inicia no primeiro ponto
        self.pos_base = [self.base_path[0][0], self.base_path[0][1]]
        self.hp = 3
        self.speed = 1.0
        self.reward = 5

        # Placeholder circular (será sobrescrito pelas classes filhas)
        size = max(int(ENEMY_BASE_SIZE * SCALE), 1)
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(img, (200, 50, 50), (size // 2, size // 2), size // 2)
        self.image = img
        self.rect = self.image.get_rect()

    def update(self):
        # Se já chegou ao último waypoint, reduz vida e mata o sprite
        if self.waypoint + 1 >= len(self.base_path):
            game_state.lose_life()
            self.kill()
            return

        # Próximo waypoint (em base)
        target_base = self.base_path[self.waypoint + 1]
        dx = target_base[0] - self.pos_base[0]
        dy = target_base[1] - self.pos_base[1]
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.waypoint += 1
        else:
            self.pos_base[0] += dx / dist * self.speed
            self.pos_base[1] += dy / dist * self.speed

        # Converte posição base → posição em tela (via SCALE_X e SCALE_Y)
        from config import SCALE_X, SCALE_Y
        real_x = int(self.pos_base[0] * SCALE_X)
        real_y = int(self.pos_base[1] * SCALE_Y)
        self.rect.center = (real_x, real_y)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()
            game_state.earn(self.reward)

class BasicEnemy(Enemy):
    def __init__(self, level_index=0):
        super().__init__(level_index)
        self.hp = 5
        self.speed = 1.0 + random.uniform(0, 0.3)
        self.reward = ENEMY_REWARD["BasicEnemy"]

        img = pygame.image.load("assets/enemy_basic.png").convert_alpha()
        # 1) escala para (ENEMY_BASE_SIZE × ENEMY_BASE_SIZE)
        img = pygame.transform.scale(img, (ENEMY_BASE_SIZE, ENEMY_BASE_SIZE))
        # 2) escala para (ENEMY_BASE_SIZE × SCALE)
        size = max(int(ENEMY_BASE_SIZE * SCALE), 1)
        self.image = pygame.transform.scale(img, (size, size))
        self.rect = self.image.get_rect()

class FastEnemy(Enemy):
    def __init__(self, level_index=0):
        super().__init__(level_index)
        self.hp = 3
        self.speed = 2.0
        self.reward = ENEMY_REWARD["FastEnemy"]

        img = pygame.image.load("assets/enemy_fast.png").convert_alpha()
        img = pygame.transform.scale(img, (ENEMY_BASE_SIZE, ENEMY_BASE_SIZE))
        size = max(int(ENEMY_BASE_SIZE * SCALE), 1)
        self.image = pygame.transform.scale(img, (size, size))
        self.rect = self.image.get_rect()
