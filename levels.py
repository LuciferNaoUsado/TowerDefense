# levels.py

import pygame
import random
from enemies import BasicEnemy, FastEnemy
from config import (
    INTRA_WAVE_DELAY,
    INTRA_WAVE_RANDOM,
    INTER_WAVE_DELAY,
    INTER_WAVE_RANDOM
)

class LevelManager:
    """
    Gerencia spawn de inimigos em “ondas” (waves) com:
      - intervalo entre cada inimigo em uma mesma onda (intra-wave),
      - intervalo entre o fim de uma onda e o início da próxima (inter-wave),
      - randomização leve nesses intervalos.
    """

    def __init__(self, waves):
        """
        waves: lista de tuplas [(EnemyClass, quantidade), …]
        """
        self.waves = waves
        self.current_wave = 0
        # Evento único para todos os spawns
        self.spawn_event = pygame.USEREVENT + 1
        self.finished = False

        # Estado interno:
        self._intra_queue = []            # fila de EnemyClasses a spawnar na wave atual
        self._waiting_inter_delay = False # sinaliza se estamos aguardando inter-wave

    def start_level(self):
        """
        Inicia o level: prepara a primeira wave e agenda o primeiro spawn.
        """
        self.current_wave = 0
        self.finished = False
        self._waiting_inter_delay = False

        # Prepara a fila da primeira wave
        self._prepare_wave()
        # Agenda o primeiro spawn (intra-wave)
        self._schedule_next_spawn()

    def _prepare_wave(self):
        """
        Carrega _intra_queue com N cópias de EnemyClass da wave atual.
        """
        EnemyClass, quantity = self.waves[self.current_wave]
        self._intra_queue = [EnemyClass] * quantity

    def _schedule_next_spawn(self):
        """
        Agenda o próximo evento self.spawn_event após um intervalo calculado:
          - Se ainda houver inimigos em _intra_queue, intervalo intra-wave:
            INTRA_WAVE_DELAY ± INTRA_WAVE_RANDOM
          - Senão, se houver próxima wave, intervalo inter-wave:
            INTER_WAVE_DELAY ± INTER_WAVE_RANDOM
        """
        # Desliga qualquer timer anterior para evitar duplicatas
        pygame.time.set_timer(self.spawn_event, 0)

        if self._intra_queue:
            # Ainda há inimigos nesta wave → intervalo intra-wave
            base = INTRA_WAVE_DELAY
            jitter = random.uniform(-INTRA_WAVE_RANDOM, INTRA_WAVE_RANDOM)
            interval = max(int(base + jitter), 50)
        else:
            # Fim da wave atual → se houver próxima wave, intervalo inter-wave
            base = INTER_WAVE_DELAY
            jitter = random.uniform(-INTER_WAVE_RANDOM, INTER_WAVE_RANDOM)
            interval = max(int(base + jitter), 100)

        pygame.time.set_timer(self.spawn_event, interval)

    def spawn_next(self, enemies_group, level_index=0):
        """
        Chamado quando self.spawn_event é capturado no main loop:
        1) Se _intra_queue não vazio → spawna 1 inimigo, depois agenda próximo intra-wave
        2) Se _intra_queue vazio e _waiting_inter_delay == False → acabou a wave, inicia inter-wave
        3) Se _waiting_inter_delay == True → inter-wave acabou, avança para próxima wave ou finaliza
        """
        # Desliga o timer atual para evitar múltiplos triggers
        pygame.time.set_timer(self.spawn_event, 0)

        # 1) Spawn individual dentro da wave
        if self._intra_queue:
            EnemyClass = self._intra_queue.pop(0)
            enemies_group.add(EnemyClass(level_index))

            # Se ainda restam inimigos nesta wave, agenda próximo intra-wave
            if self._intra_queue:
                self._schedule_next_spawn()
            else:
                # Esta wave terminou; agora aguardaremos o intervalo inter-wave
                self._waiting_inter_delay = True
                self._schedule_next_spawn()
            return

        # 2) Se _intra_queue está vazio e estamos aguardando inter-wave
        if self._waiting_inter_delay:
            self._waiting_inter_delay = False
            self.current_wave += 1

            if self.current_wave < len(self.waves):
                # Há próxima wave: prepara e spawna o primeiro inimigo
                self._prepare_wave()
                self._schedule_next_spawn()
            else:
                # Não há mais waves: marca nível como finalizado
                self.finished = True
            return

        # 3) Senão (possível chamada indevida), não faz nada
        return


# === Definição das ondas em cada nível ===
# Cada nível é uma LISTA DE TUPLAS (ClasseDeInimigo, quantidade)
LEVELS = [
    # ===== Level 1 =====
    [
        (BasicEnemy, 2),  # wave 1: 2 BasicEnemy
        (BasicEnemy, 3),  # wave 2: 3 BasicEnemy
        (BasicEnemy, 5),  # wave 3: 5 BasicEnemy
    ],

    # ===== Level 2 =====
    [
        (BasicEnemy, 4),
        (FastEnemy, 4),
    ],

    # Você pode adicionar mais níveis seguindo o mesmo formato
]
