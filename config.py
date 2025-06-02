# config.py

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# RESOLUÇÃO BASE (NÃO ALTERAR)
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
BASE_WIDTH  = 1536
BASE_HEIGHT = 1024

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# RESOLUÇÃO ATUAL DA JANELA (INICIAL, PODE SER REDIMENSIONADA)
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 900

# — FPS —
FPS = 60

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# VARIÁVEIS DE ESCALA (RECALCULADAS NO update_screen_size)
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
SCALE_X = SCREEN_WIDTH  / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
SCALE   = min(SCALE_X, SCALE_Y)

# — Cores de fallback para desenhar o path manualmente, se necessário —
BG_COLOR   = (30, 30, 30)
PATH_COLOR = (60, 60, 60)

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# DINHEIRO INICIAL E CUSTOS DE TORRES/UPGRADES
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
INITIAL_MONEY = 200

TOWER_COSTS = {
    "BasicTower": 50,
    "SniperTower": 100,
}

UPGRADE_COSTS = {
    "BasicTower": [30, 50],    # custo do nível 1→2 = 30, do nível 2→3 = 50
    "SniperTower": [60, 100],  # custo do nível 1→2 = 60, do nível 2→3 = 100
}

# — Recompensa por matar cada tipo de inimigo —
ENEMY_REWARD = {
    "BasicEnemy": 10,
    "FastEnemy": 15,
}

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# TEMPO ENTRE SPAWNS DE INIMIGOS E ENTRE ONDAS
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# Tempo (ms) base entre inimigos de uma mesma onda (intra‐wave)
INTRA_WAVE_DELAY = 1000

# Variabilidade (± ms) para o intervalo entre inimigos
INTRA_WAVE_RANDOM = 200

# Tempo (ms) base entre o fim de uma onda e o início da próxima (inter‐wave)
INTER_WAVE_DELAY = 10000

# Variabilidade (± ms) para o intervalo entre ondas
INTER_WAVE_RANDOM = 800

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# Arquivos de fundo de cada nível (cada um deve ter exatos 1536×1024 px)
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
BACKGROUND_FILES = [
    "assets/L1.png",
    "assets/L2.png",  # se houver Level 2
]

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# TAMANHOS “BASE” DOS SPRITES NA RESOLUÇÃO 1536×1024
# Cada sprite será escalado para (BASE_SIZE × SCALE) na janela atual
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
ENEMY_BASE_SIZE  = 48    # inimigos serão 48×48 na base
TOWER_BASE_SIZE  = 64    # torres serão 64×64 na base
BULLET_BASE_SIZE = 24    # projéteis serão 24×24 na base

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# ÍCONES (HUD) – tamanho em px na base 1536×1024
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
ICON_BASE_SIZE = 24     # ícones de dinheiro/vida 24×24 na base

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# Função para atualizar resolução e recalcular SCALE_X, SCALE_Y, SCALE
# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
def update_screen_size(new_width: int, new_height: int):
    """
    Chamado sempre que a janela for redimensionada (evento VIDEORESIZE).
    Recalcula SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_X, SCALE_Y e SCALE.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_X, SCALE_Y, SCALE

    SCREEN_WIDTH = new_width
    SCREEN_HEIGHT = new_height

    SCALE_X = SCREEN_WIDTH / BASE_WIDTH
    SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
    SCALE   = min(SCALE_X, SCALE_Y)
