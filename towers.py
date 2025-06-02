# towers.py

import pygame
import math
from config import TOWER_COSTS, UPGRADE_COSTS, SCALE, SCALE_X, SCALE_Y, TOWER_BASE_SIZE
from bullets import BasicBullet
from game_state import game_state

class Tower(pygame.sprite.Sprite):
    # Cada subtipo define seu próprio BASE_RANGE (em px na base 1536×1024)
    BASE_RANGE = 100

    def __init__(self, pos_base):
        """
        pos_base: (x, y) em coordenadas base (1536×1024) onde o jogador clicou.
        """
        super().__init__()
        self.pos_base = list(pos_base)
        self.level = 1

        # Carrega “tower_basic.png” (digamos 32×32), redimensiona para (TOWER_BASE_SIZE × TOWER_BASE_SIZE)
        img = pygame.image.load("assets/tower_basic.png").convert_alpha()
        img = pygame.transform.scale(img, (TOWER_BASE_SIZE, TOWER_BASE_SIZE))
        # Agora redimensiona para a tela: (int(TOWER_BASE_SIZE×SCALE) × int(TOWER_BASE_SIZE×SCALE))
        size = max(int(TOWER_BASE_SIZE * SCALE), 1)
        self.image = pygame.transform.scale(img, (size, size))
        self.rect = self.image.get_rect()
        self._update_rect()

        self.cost = TOWER_COSTS[self.__class__.__name__]
        self.range = int(self.BASE_RANGE * SCALE)

        # Fire rate (ms) e temporizador
        self.fire_rate = 1000
        self.last_shot = pygame.time.get_ticks()

    def _update_rect(self):
        """Atualiza self.rect.center conforme pos_base convertido para tela."""
        real_x = int(self.pos_base[0] * SCALE_X)
        real_y = int(self.pos_base[1] * SCALE_Y)
        self.rect.center = (real_x, real_y)

    def update(self):
        # Toda vez que for chamado update(), reposiciona o rect (se SCALE mudou)
        self._update_rect()

    def try_shoot(self, enemies_group, bullets_group):
        """Procura inimigo mais próximo dentro do range e dispara, respeitando fire_rate."""
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.fire_rate:
            return

        real_center = self.rect.center
        target = None
        min_dist = float("inf")
        for enemy in enemies_group:
            ex, ey = enemy.rect.center
            dist = math.hypot(ex - real_center[0], ey - real_center[1])
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                target = enemy

        if target:
            bullet = BasicBullet(real_center, target)
            bullets_group.add(bullet)
            self.last_shot = now

    def upgrade(self):
        """
        Realiza upgrade:
        - Aumenta self.level até 3
        - Aumenta self.range (×1.2 por nível)
        - Custa UPGRADE_COSTS[classe][self.level - 1]
        - (Opcional) trocar sprite se houver versão para nível superior
        """
        name = self.__class__.__name__
        if self.level < 3:
            custo = UPGRADE_COSTS[name][self.level - 1]
            if game_state.can_afford(custo):
                game_state.spend(custo)
                self.level += 1
                self.range = int(self.range * 1.2)
                # Se quiser trocar sprite para level maior, faça aqui (ex. tower_basic_lv2.png)
                # img_lv2 = pygame.image.load("assets/tower_basic_lv2.png").convert_alpha()
                # img_lv2 = pygame.transform.scale(img_lv2, (TOWER_BASE_SIZE, TOWER_BASE_SIZE))
                # size = max(int(TOWER_BASE_SIZE * SCALE), 1)
                # self.image = pygame.transform.scale(img_lv2, (size, size))
                # self.rect = self.image.get_rect()
                # self._update_rect()

class BasicTower(Tower):
    COST = TOWER_COSTS["BasicTower"]
    BASE_RANGE = 100
    def __init__(self, pos_base):
        super().__init__(pos_base)
        # A classe-mãe já carrega “tower_basic.png” e redimensiona

class SniperTower(Tower):
    COST = TOWER_COSTS["SniperTower"]
    BASE_RANGE = 200
    def __init__(self, pos_base):
        super().__init__(pos_base)
        img = pygame.image.load("assets/tower_sniper.png").convert_alpha()
        img = pygame.transform.scale(img, (TOWER_BASE_SIZE, TOWER_BASE_SIZE))
        size = max(int(TOWER_BASE_SIZE * SCALE), 1)
        self.image = pygame.transform.scale(img, (size, size))
        self.rect = self.image.get_rect()
        self._update_rect()

        self.range = int(self.BASE_RANGE * SCALE)
        self.fire_rate = 1500  # dispara a cada 1.5s
