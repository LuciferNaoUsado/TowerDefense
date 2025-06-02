# main.py

import pygame
import sys
import pygame.freetype

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BACKGROUND_FILES,
    BG_COLOR,
    INITIAL_MONEY,
    SCALE,
    SCALE_X,
    SCALE_Y,
    ICON_BASE_SIZE,       # <– importe a constante aqui
    update_screen_size
)
from game_state import game_state
from levels import LevelManager, LEVELS
from towers import BasicTower, SniperTower
from enemies import BasicEnemy, FastEnemy
from bullets import BasicBullet, HeavyBullet
import paths   # contém PATHS em base 1536×1024

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("Tower Defense Modular (Redimensionável)")
    clock = pygame.time.Clock()
    fonte = pygame.freetype.SysFont(None, max(int(24 * SCALE), 1))

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # CARREGA OS MAPAS (FUNDOS) E ARMAZENA A VERSÃO ORIGINAL (1536×1024)
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    background_srcs = []
    for file in BACKGROUND_FILES:
        bg_src = pygame.image.load(file).convert()
        background_srcs.append(bg_src)

    # Escalona pela primeira vez para a janela inicial
    background_imgs = []
    for bg_src in background_srcs:
        bg_scaled = pygame.transform.scale(bg_src, (SCREEN_WIDTH, SCREEN_HEIGHT))
        background_imgs.append(bg_scaled)

    current_level = 0
    max_level_index = len(BACKGROUND_FILES) - 1

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # PREPARA O LevelManager PARA SPAWN DE INIMIGOS
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    level_manager = LevelManager(LEVELS[current_level])
    level_manager.start_level()
    SPAWN_ENEMY = level_manager.spawn_event

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # GRUPOS DE SPRITES
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    enemies = pygame.sprite.Group()
    towers  = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    selected_tower_type = BasicTower

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # CONFIGURA BOTÃO “PRÓXIMA FASE”
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    show_next_button = False
    btn_w = max(int(170 * SCALE), 1)
    btn_h = max(int(30  * SCALE), 1)
    button_rect = pygame.Rect(
        SCREEN_WIDTH - btn_w - max(int(10 * SCALE), 1),
        max(int(10 * SCALE), 1),
        btn_w,
        btn_h
    )
    button_color = (200, 50, 50)
    button_text_color = (255, 255, 255)

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # MENU DE SELEÇÃO DE TORRE
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    show_tower_menu = False
    click_x_base = click_y_base = 0
    menu_lines = [
        ("Basic Tower", BasicTower.COST),
        ("Sniper Tower", SniperTower.COST),
    ]
    menu_padding_x = max(int(16 * SCALE), 1)
    menu_padding_y = max(int(8  * SCALE), 1)
    line_spacing  = max(int(6  * SCALE), 1)

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # CARREGA ÍCONES DE DINHEIRO E VIDA (somente uma vez, ARMAZENA A VERSÃO ORIGINAL)
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    try:
        icon_money_src = pygame.image.load("assets/money_icon.png").convert_alpha()
    except:
        icon_money_src = pygame.Surface((1, 1), pygame.SRCALPHA)

    try:
        icon_life_src  = pygame.image.load("assets/life_icon.png").convert_alpha()
    except:
        icon_life_src  = pygame.Surface((1, 1), pygame.SRCALPHA)

    # Redimensiona os ícones pela primeira vez, usando ICON_BASE_SIZE × SCALE
    size_icon = max(int(ICON_BASE_SIZE * SCALE), 1)
    icon_money = pygame.transform.scale(icon_money_src, (size_icon, size_icon))
    icon_life  = pygame.transform.scale(icon_life_src,  (size_icon, size_icon))

    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    # INICIALIZA DINHEIRO E VIDAS
    # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
    game_state.money = INITIAL_MONEY
    game_state.lives = 10

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            # … (demais eventos, inclusive DEBUG, QUIT, RESIZE, SPAWN, CLIQUES) …

            # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
            # TRATAMENTO DO EVENTO VIDEORESIZE (janela redimensionada)
            # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
            if event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.w, event.h
                if new_w < 200: new_w = 200
                if new_h < 150: new_h = 150

                # 1) Atualiza valores em config (isto recalcula SCALE_X, SCALE_Y e SCALE)
                update_screen_size(new_w, new_h)

                # 2) Redefine a janela com o novo tamanho
                screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                    pygame.RESIZABLE
                )

                # 3) Reescalona todos os mapas (originais em background_srcs)
                background_imgs = []
                for bg_src in background_srcs:
                    bg_scaled = pygame.transform.scale(bg_src, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    background_imgs.append(bg_scaled)

                # 4) Recalcula botão “Próxima Fase”
                btn_w = max(int(170 * SCALE), 1)
                btn_h = max(int(30  * SCALE), 1)
                button_rect = pygame.Rect(
                    SCREEN_WIDTH - btn_w - max(int(10 * SCALE), 1),
                    max(int(10 * SCALE), 1),
                    btn_w,
                    btn_h
                )

                # 5) **Reescalona os ícones de acordo com o novo SCALE**
                size_icon = max(int(ICON_BASE_SIZE * SCALE), 1)
                icon_money = pygame.transform.scale(icon_money_src, (size_icon, size_icon))
                icon_life  = pygame.transform.scale(icon_life_src,  (size_icon, size_icon))

                # 6) Recria a fonte para a escala atual
                fonte = pygame.freetype.SysFont(None, max(int(24 * SCALE), 1))

                continue  # vai para o próximo evento

            # … (restante do loop de eventos) …

        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
        # ATUALIZAÇÃO DE SPRITES
        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
        enemies.update()
        towers.update()
        bullets.update()
        for torre in towers:
            torre.try_shoot(enemies, bullets)

        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
        # EXIBE PRÓXIMA FASE SE PRESSIONADO
        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
        # … (lógica para mostrar botão de próxima fase) …

        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
        # FASE DE DESENHO
        # —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—

        # 1) Desenha fundo do nível atual
        if current_level <= max_level_index:
            screen.blit(background_imgs[current_level], (0, 0))
        else:
            screen.fill(BG_COLOR)

        # 2) Desenha o caminho (path)
        if current_level < len(paths.PATHS):
            paths.draw_path(current_level, screen)

        # 3) Desenha inimigos, torres e projéteis
        enemies.draw(screen)
        towers.draw(screen)
        bullets.draw(screen)

        # 4) HUD: Ícone de dinheiro + texto
        hud_x = max(int(10 * SCALE), 1)
        hud_y = max(int(10 * SCALE), 1)
        screen.blit(icon_money, (hud_x, hud_y))
        fonte.render_to(
            screen,
            (hud_x + size_icon + max(int(5 * SCALE), 1), hud_y + max(int(2 * SCALE), 1)),
            f"x {game_state.money}",
            (240, 240, 240)
        )

        # 5) HUD: Ícone de vida + texto (logo abaixo)
        hud_y2 = hud_y + size_icon + max(int(4 * SCALE), 1)
        screen.blit(icon_life, (hud_x, hud_y2))
        fonte.render_to(
            screen,
            (hud_x + size_icon + max(int(5 * SCALE), 1), hud_y2 + max(int(2 * SCALE), 1)),
            f"x {game_state.lives}",
            (240, 240, 240)
        )

        # 6) Botão “Próxima Fase” (se ativo)
        if show_next_button and (current_level < max_level_index):
            pygame.draw.rect(screen, button_color, button_rect, border_radius=max(int(4 * SCALE), 1))
            fonte.render_to(
                screen,
                (button_rect.x + max(int(12 * SCALE), 1), button_rect.y + max(int(5 * SCALE), 1)),
                "Próxima Fase",
                button_text_color
            )

        # 7) Menu de seleção de torre (popup) — desenhado sobre o resto…
        if show_tower_menu:
            # … (código para desenhar o balão com opções) …
            pass

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
