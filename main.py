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
    ICON_BASE_SIZE,
    update_screen_size
)
from game_state import game_state
from levels import LevelManager, LEVELS
from towers import BasicTower, SniperTower
from enemies import BasicEnemy, FastEnemy
from bullets import BasicBullet
import paths   # contém PATHS em base 1536×1024

def main():
    pygame.init()

    # Cria janela redimensionável
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("Tower Defense Modular (Redimensionável)")
    clock = pygame.time.Clock()
    fonte = pygame.freetype.SysFont(None, max(int(24 * SCALE), 1))

    # ===============================
    # 1) CARREGA MAPAS (FUNDOS) E ARMAZENA IMAGENS ORIGINAIS
    # ===============================
    background_srcs = []
    for file in BACKGROUND_FILES:
        bg_src = pygame.image.load(file).convert()  # original 1536×1024
        background_srcs.append(bg_src)

    # Escalonamos pela primeira vez para a resolução inicial
    background_imgs = []
    for bg_src in background_srcs:
        bg_scaled = pygame.transform.scale(bg_src, (SCREEN_WIDTH, SCREEN_HEIGHT))
        background_imgs.append(bg_scaled)

    current_level = 0
    max_level_index = len(BACKGROUND_FILES) - 1

    # ===============================
    # 2) PREPARA LevelManager PARA AS ONDAS DO NÍVEL ATUAL
    # ===============================
    level_manager = LevelManager(LEVELS[current_level])
    level_manager.start_level()
    SPAWN_ENEMY = level_manager.spawn_event

    # ===============================
    # 3) GRUPOS DE SPRITES
    # ===============================
    enemies = pygame.sprite.Group()
    towers  = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    selected_tower_type = BasicTower

    # ===============================
    # 4) CONFIGURA BOTÃO “PRÓXIMA FASE”
    # ===============================
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

    # ===============================
    # 5) CONFIGURA MENU DE SELEÇÃO DE TORRE
    # ===============================
    show_tower_menu = False
    click_x_base = click_y_base = 0
    menu_lines = [
        ("Basic Tower", BasicTower.COST),
        ("Sniper Tower", SniperTower.COST),
    ]
    menu_padding_x = max(int(16 * SCALE), 1)
    menu_padding_y = max(int(8  * SCALE), 1)
    line_spacing  = max(int(6  * SCALE), 1)

    # ===============================
    # 6) CARREGA ÍCONES DE DINHEIRO E VIDA (ARMAZENA ORIGINAIS)
    # ===============================
    try:
        icon_money_src = pygame.image.load("assets/money_icon.png").convert_alpha()
    except:
        icon_money_src = pygame.Surface((1, 1), pygame.SRCALPHA)

    try:
        icon_life_src  = pygame.image.load("assets/life_icon.png").convert_alpha()
    except:
        icon_life_src  = pygame.Surface((1, 1), pygame.SRCALPHA)

    # Redimensiona pela primeira vez para (ICON_BASE_SIZE × SCALE)
    size_icon = max(int(ICON_BASE_SIZE * SCALE), 1)
    icon_money = pygame.transform.scale(icon_money_src, (size_icon, size_icon))
    icon_life  = pygame.transform.scale(icon_life_src,  (size_icon, size_icon))

    # ===============================
    # 7) INICIALIZA DINHEIRO E VIDAS
    # ===============================
    game_state.money = INITIAL_MONEY
    game_state.lives = 10

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            # ———————————————
            # SAIR DO JOGO
            # ———————————————
            if event.type == pygame.QUIT:
                running = False
                break  # sai do loop de eventos imediatamente

            # ———————————————
            # REDIMENSIONAMENTO DA JANELA
            # ———————————————
            if event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.w, event.h
                if new_w < 200: new_w = 200
                if new_h < 150: new_h = 150

                # 1) Atualiza variáveis em config (SCALE_X, SCALE_Y, SCALE)
                update_screen_size(new_w, new_h)

                # 2) Redefine a janela para a nova resolução
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

                # 5) Reescalona ícones de HUD
                size_icon = max(int(ICON_BASE_SIZE * SCALE), 1)
                icon_money = pygame.transform.scale(icon_money_src, (size_icon, size_icon))
                icon_life  = pygame.transform.scale(icon_life_src,  (size_icon, size_icon))

                # 6) Recria a fonte na escala atual
                fonte = pygame.freetype.SysFont(None, max(int(24 * SCALE), 1))

                continue  # segue para o próximo evento

            # ———————————————
            # SPAWN DE INIMIGOS (evento do LevelManager)
            # ———————————————
            if event.type == SPAWN_ENEMY:
                # Gera o próximo spawn (intra‐wave ou inter‐wave)
                level_manager.spawn_next(enemies, level_index=current_level)

            # ———————————————
            # CLIQUE ESQUERDO (BOTÃO 1)
            # ———————————————
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                # 7.1) Clique no botão “Próxima Fase”?
                if (show_next_button
                    and (current_level < max_level_index)
                    and button_rect.collidepoint((mx, my))):
                    # Avança para o próximo nível
                    current_level += 1
                    game_state.money = INITIAL_MONEY
                    game_state.lives = 10
                    towers.empty()
                    bullets.empty()
                    enemies.empty()
                    level_manager = LevelManager(LEVELS[current_level])
                    level_manager.start_level()
                    SPAWN_ENEMY = level_manager.spawn_event
                    show_next_button = False
                    show_tower_menu = False
                    continue

                # 7.2) Se o menu de torre já está aberto
                if show_tower_menu:
                    # Recalcular dimensões do balão
                    max_text_width = 0
                    text_height = 0
                    rendered_texts = []
                    for name, cost in menu_lines:
                        txt = f"{name} (${cost})"
                        surf, _ = fonte.render(txt, (255, 255, 255))
                        rendered_texts.append(surf)
                        max_text_width = max(max_text_width, surf.get_width())
                        text_height = max(text_height, surf.get_height())

                    menu_width = max_text_width + 2 * menu_padding_x
                    menu_height = len(menu_lines) * text_height + 2 * menu_padding_y + (len(menu_lines) - 1) * line_spacing

                    real_menu_x = int(click_x_base * SCALE_X) + max(int(10 * SCALE), 1)
                    real_menu_y = int(click_y_base * SCALE_Y)
                    menu_rect = pygame.Rect(real_menu_x, real_menu_y, menu_width, menu_height)

                    # Se clicou fora do balão, fecha-o sem comprar
                    if not menu_rect.collidepoint((mx, my)):
                        show_tower_menu = False
                        continue

                    # Se clicou dentro, determina a linha que foi clicada
                    rel_y = my - real_menu_y - menu_padding_y
                    line_h = text_height + line_spacing
                    clicked_line = rel_y // line_h
                    if 0 <= clicked_line < len(menu_lines):
                        name, cost = menu_lines[int(clicked_line)]
                        if game_state.can_afford(cost):
                            game_state.spend(cost)
                            if name == "Basic Tower":
                                towers.add(BasicTower((click_x_base, click_y_base)))
                            else:
                                towers.add(SniperTower((click_x_base, click_y_base)))
                        show_tower_menu = False
                    continue

                # 7.3) Senão, abre o menu de seleção de torre
                click_x_base = int(mx / SCALE_X)
                click_y_base = int(my / SCALE_Y)
                show_tower_menu = True

            # ———————————————
            # CLIQUE DIREITO (BOTÃO 3) = upgrade na torre sob o mouse
            # ———————————————
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mx, my = pygame.mouse.get_pos()
                for torre in towers:
                    if torre.rect.collidepoint((mx, my)):
                        torre.upgrade()
                        break

            # ———————————————
            # TECLAS 1 e 2 PARA SELEÇÃO RÁPIDA DE TORRE (OPCIONAL)
            # ———————————————
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_tower_type = BasicTower
                elif event.key == pygame.K_2:
                    selected_tower_type = SniperTower

        # Se o usuário clicou em “quit”, break do while principal
        if not running:
            break

        # ===============================
        # 8) ATUALIZAÇÃO DE SPRITES
        # ===============================
        enemies.update()
        towers.update()
        bullets.update()

        for torre in towers:
            torre.try_shoot(enemies, bullets)

        # ===============================
        # 9) LÓGICA DO BOTÃO “PRÓXIMA FASE”
        # ===============================
        if (level_manager.finished
            and (len(enemies) == 0)
            and (current_level < max_level_index)):
            show_next_button = True
        else:
            show_next_button = False

        # ===============================
        # 10) FASE DE DESENHO
        # ===============================

        # 11) DESENHA O FUNDO DO NÍVEL ATUAL (mapa escalado)
        if current_level <= max_level_index:
            screen.blit(background_imgs[current_level], (0, 0))
        else:
            screen.fill(BG_COLOR)

        # 12) DESENHA O “PATH” (caminho cinza)
        if current_level < len(paths.PATHS):
            paths.draw_path(current_level, screen)

        # 13) DESENHA INIMIGOS, TORRES E PROJÉTEIS
        enemies.draw(screen)
        towers.draw(screen)
        bullets.draw(screen)

        # 14) HUD: ÍCONES DE DINHEIRO E VIDA + TEXTO
        hud_x = max(int(10 * SCALE), 1)
        hud_y = max(int(10 * SCALE), 1)
        screen.blit(icon_money, (hud_x, hud_y))
        fonte.render_to(
            screen,
            (hud_x + size_icon + max(int(5 * SCALE), 1), hud_y + max(int(2 * SCALE), 1)),
            f"x {game_state.money}",
            (240, 240, 240)
        )

        hud_y2 = hud_y + size_icon + max(int(4 * SCALE), 1)
        screen.blit(icon_life, (hud_x, hud_y2))
        fonte.render_to(
            screen,
            (hud_x + size_icon + max(int(5 * SCALE), 1), hud_y2 + max(int(2 * SCALE), 1)),
            f"x {game_state.lives}",
            (240, 240, 240)
        )

        # 15) BOTÃO “PRÓXIMA FASE” (se for para exibir)
        if show_next_button and (current_level < max_level_index):
            pygame.draw.rect(screen, button_color, button_rect, border_radius=max(int(4 * SCALE), 1))
            fonte.render_to(
                screen,
                (button_rect.x + max(int(12 * SCALE), 1), button_rect.y + max(int(5 * SCALE), 1)),
                "Próxima Fase",
                button_text_color
            )

        # 16) MENU DE SELEÇÃO DE TORRE (POPUP)
        if show_tower_menu:
            # 16.1) Mede dimensões do texto para criar o balão
            max_text_width = 0
            text_height = 0
            rendered_texts = []
            for name, cost in menu_lines:
                txt = f"{name} (${cost})"
                surf, _ = fonte.render(txt, (255, 255, 255))
                rendered_texts.append(surf)
                max_text_width = max(max_text_width, surf.get_width())
                text_height = max(text_height, surf.get_height())

            menu_width = max_text_width + 2 * menu_padding_x
            menu_height = len(menu_lines) * text_height + 2 * menu_padding_y + (len(menu_lines) - 1) * line_spacing

            real_menu_x = int(click_x_base * SCALE_X) + max(int(10 * SCALE), 1)
            real_menu_y = int(click_y_base * SCALE_Y)

            # 16.2) Desenha retângulo semi-transparente atrás do balão
            overlay = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (real_menu_x, real_menu_y))

            # 16.3) Desenha cada linha de texto centralizada
            y_offset = real_menu_y + menu_padding_y
            for text_surf in rendered_texts:
                x_offset = real_menu_x + (menu_width - text_surf.get_width()) // 2
                screen.blit(text_surf, (x_offset, y_offset))
                y_offset += text_height + line_spacing

        pygame.display.flip()

    # Quando sair do loop principal:
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
