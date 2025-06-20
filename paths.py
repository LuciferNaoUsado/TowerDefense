# paths.py

import pygame
from config import PATH_COLOR, SCALE_X, SCALE_Y

# Cada lista em PATHS[] é a sequência de waypoints (x, y) na base 1536×1024
PATHS = [
    # ===== Level 1 =====
    [
        (-50, 1014),   # 1) Entrada fora da tela à esquerda
        (200,  800),   # 2) Vai para (200,800)
        (600,  800),   # 3) Vai para (600,800)
        (600,  600),   # 4) Vai para (600,600)
        (1000, 600),   # 5) Vai para (1000,600)
        (1000, 200),   # 6) Vai para (1000,200)
        (1400, 200),   # 7) Vai para (1400,200)
        (1586, 200),   # 8) Saída fora da tela à direita
    ],

    # ===== Level 2 =====
    # [
    #     (-50, 500),
    #     (300, 500),
    #     (300, 300),
    #     (900, 300),
    #     (900, 700),
    #     (1586, 700)
    # ],
]

def draw_path(level_index: int, surface: pygame.Surface):
    """
    Desenha o “path” ligando cada waypoint de PATHS[level_index].
    Converte coordenadas base (1536×1024) → coordenadas de tela (via SCALE_X e SCALE_Y).
    """
    if level_index < 0 or level_index >= len(PATHS):
        return

    path = PATHS[level_index]
    from config import SCALE
    thickness = max(int(40 * SCALE), 1)  # espessura base = 40 px, escalonada

    # Converte (x_base, y_base) → (x_tela, y_tela)
    scaled_points = [
        (int(x * SCALE_X), int(y * SCALE_Y))
        for (x, y) in path
    ]

    for i in range(len(scaled_points) - 1):
        p1 = scaled_points[i]
        p2 = scaled_points[i + 1]
        pygame.draw.line(surface, PATH_COLOR, p1, p2, thickness)
