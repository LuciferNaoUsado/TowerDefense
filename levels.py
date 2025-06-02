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
    Gerencia o spawn de inimigos em “ondas” (waves) com:
      - intervalo entre cada inimigo em uma mesma onda (intra-wave),
      - intervalo entre o fim de uma onda e o início da próxima (inter-wave),
      - randomização leve nesses intervalos.
    """

    def __init__(self, waves):
        """
        waves: lista de tuplas [(EnemyClass, quantidade), ...]
        """
        self.waves = waves
        self.current_wave = 0
        # Vamos usar um evento fixo para todos os spawns
        self.spawn_event = pygame.USEREVENT + 1
        self.finished = False

        # --- Estado interno para controlar spawn dentro da wave ---
        self._intra_queue = []           # fila de EnemyClasses a serem gerados na onda atual
        self._waiting_inter_delay = False  # sinaliza se estamos aguardando inter-wave

    def start_level(self):
        """
        Inicia o nivel: prepara a wave 0 e marca um timer para spawn do 1º inimigo.
        """
        self.current_wave = 0
        self.finished = False
        self._waiting_inter_delay = False

        # Prepara a fila de inimigos da primeira wave
        self._prepare_wave()
        # Agenda o primeiro spawn (usando intervalo intra-wave)
        self._schedule_next_spawn()

    def _prepare_wave(self):
        """
        Carrega a lista interna _intra_queue com N cópias de EnemyClass da wave atual.
        """
        EnemyClass, quantity = self.waves[self.current_wave]
        self._intra_queue = [EnemyClass] * quantity

    def _schedule_next_spawn(self):
        """
        Agenda o próximo evento self.spawn_event após um intervalo calculado:
         - Se estiver dentro de uma wave (com _intra_queue não vazia), usa
           INTRA_WAVE_DELAY ± INTRA_WAVE_RANDOM
         - Se _intra_queue acabou e ainda existem waves, usa
           INTER_WAVE_DELAY ± INTER_WAVE_RANDOM
         - Se for fornecido delay extra (não há argumento aqui), poderíamos usar ele diretamente.
        """
        # Cancelamos qualquer timer anterior para evitar duplicatas
        pygame.time.set_timer(self.spawn_event, 0)

        if self._intra_queue:
            # Ainda existem inimigos nesta wave → intervalo intra-wave
            base = INTRA_WAVE_DELAY
            jitter = random.uniform(-INTRA_WAVE_RANDOM, INTRA_WAVE_RANDOM)
            interval = max(int(base + jitter), 50)  # mínimo 50ms
        else:
            # A wave atual acabou; se houver próxima wave, aguardamos intervalo inter-wave
            base = INTER_WAVE_DELAY
            jitter = random.uniform(-INTER_WAVE_RANDOM, INTER_WAVE_RANDOM)
            interval = max(int(base + jitter), 100)  # mínimo 100ms

        pygame.time.set_timer(self.spawn_event, interval)

    def spawn_next(self, enemies_group, level_index=0):
        """
        Chamado quando o evento self.spawn_event é capturado no loop principal.
        1) Se houver items em self._intra_queue, faz spawn de 1 inimigo.
            - Se ainda restarem inimigos, agenda próximo spawn intra-wave.
            - Se acabou a fila _intra_queue, agenda intervalo inter-wave e marca _waiting_inter_delay = True.
        2) Se _intra_queue vazio e _waiting_inter_delay == True:
            - Isso significa que o inter-wave delay terminou; passa para próxima wave ou finaliza.
        """
        # Desliga o timer imediatamente para evitar novos triggers duplicados
        pygame.time.set_timer(self.spawn_event, 0)

        # 1) Caso ainda existam inimigos na fila interna (intra_queue):
        if self._intra_queue:
            EnemyClass = self._intra_queue.pop(0)
            enemies_group.add(EnemyClass(level_index))

            # Ainda restam inimigos nesta wave?
            if self._intra_queue:
                # Agenda próximo spawn dentro desta mesma wave
                self._schedule_next_spawn()
            else:
                # Terminou de spawnar todos os inimigos desta wave.
                # Agora entra no estado “aguardando inter-wave”:
                self._waiting_inter_delay = True
                self._schedule_next_spawn()
            return

        # 2) Se chegou aqui, _intra_queue está vazio
        #    e estamos aguardando o inter-wave:
        if self._waiting_inter_delay:
            self._waiting_inter_delay = False
            self.current_wave += 1

            if self.current_wave < len(self.waves):
                # Ainda há próxima wave: prepara e spawna primeiro inimigo
                self._prepare_wave()
                self._schedule_next_spawn()
            else:
                # Não há mais waves: terminou o nível
                self.finished = True
            return

        # 3) Se chegou aqui e não está aguardando inter-wave, e _intra_queue vazio,
        #    significa que as waves acabaram (finished=True) ou spawn_next foi
        #    chamado indevidamente — não faz nada.
        return


# === Definição das ondas por nível ===
#    Cada nível é uma lista de (ClasseDeInimigo, quantidade)
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

    # Você pode adicionar mais níveis aqui, no mesmo formato.
]
