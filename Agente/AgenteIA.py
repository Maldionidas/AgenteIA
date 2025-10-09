# Agente/AgenteIA.py
import pygame
from config import TAM
from .energia import Energia
from .render import dibujar as dibujar_render
from .constants import (VISION, COSTO_SPRINT, COSTO_NORMAL, RECALC_COOLDOWN_MS)
from .planner import recalcular_si_conviene
from .percepcion import raton_mas_cercano

# OJO: estas 5 sí vienen de states.py
from .states import (
    ensure_runtime_flags,
    handle_bebiendo,
    handle_jugando,
    handle_sin_energia,
    handle_en_base_y_recarga,
)

# OJO: estas vienen de interacciones.py
from .interacciones import (
    end_pick_animation_if_done,
    step_on_raton,
    step_on_plato,
    step_on_estambre,
    handle_deposito,
    prioridad_plato,
    planear_si_no_hay_ruta,
    salvaguarda_energia,                     
    mantener_persecucion_o_volver_flujo,     
)

from .movimiento import mover as mover_fn

class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200, 50, 50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3

        # Ruta/objetivo
        self.ruta = []
        self.objetivo = None
        self.cargando = False
        self.fue_deposito = False
        self.contador_deposito = 0
        self.recolectadas = 0

        # Animación recoger
        self.animando = False
        self.inicio_animacion = 0
        self.tiempo_animacion = 1000
        self.estado = "Idle"

        self.font = pygame.font.SysFont(None, max(16, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        # Energía
        self.energia = Energia(energia_max=300, recarga_por_segundo=40, costo_paso=1)

        # Sprites gato
        self.images = {
            "front": pygame.transform.scale(pygame.image.load("personajes/cat_front.png").convert_alpha(), (TAM, TAM)),
            "back":  pygame.transform.scale(pygame.image.load("personajes/cat_back.png").convert_alpha(),  (TAM, TAM)),
            "left":  pygame.transform.scale(pygame.image.load("personajes/cat_left.png").convert_alpha(),  (TAM, TAM)),
            "right": pygame.transform.scale(pygame.image.load("personajes/cat_right.png").convert_alpha(), (TAM, TAM)),
        }
        self.dir = "front"

        # Sprite ratón (para render)
        raton = pygame.image.load("personajes/raton.png").convert_alpha()
        rs = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(raton, (rs, rs))

        # Timers y estados auxiliares
        self._ultimo_recalculo = 0
        self.ultimo_tick = pygame.time.get_ticks()
        self.recargando = False
        self.persiguiendo = False

    # util interno para ticks
    def _ticks(self):
        return pygame.time.get_ticks()

    # mover (delegado)
    def mover(self, accion, mapa):
        mover_fn(self, accion, mapa)

    def actualizar(self, mapa):
        # 1) flags/constantes dinámicas
        ensure_runtime_flags(self)
        self.energia.costo_paso = COSTO_SPRINT if self.persiguiendo else COSTO_NORMAL

        # 2) BEBIENDO
        if handle_bebiendo(self, mapa):
            return

        # 3) JUGANDO
        if handle_jugando(self, mapa):
            return

        # 4) SIN ENERGÍA (fuera de base)
        if handle_sin_energia(self, mapa):
            return

        # 5) Animación de recoger (si está corriendo)
        if end_pick_animation_if_done(self, mapa):
            if self.animando:  # si sigue animando, detener aquí
                return
            # si terminó, ya se programó ir a depósito; continuar flujo

        # 6) En base: recargar si hace falta
        if handle_en_base_y_recarga(self, mapa):
            return
    
        # 7) Llegó a base tras depósito: sumar recolectadas (comportamiento previo)
        if not self.cargando and self.fue_deposito and (self.fila, self.col) == self.base:
            self.recolectadas += 1
            self.fue_deposito = False
            self.objetivo = None
            self.ruta = []

        # 8) Interacciones al pisar celda (ratón, plato, estambre)
        if step_on_raton(self, mapa):
            return
        if step_on_plato(self, mapa):
            return
        if step_on_estambre(self, mapa):
            return

        # 9) Depósito (si llegó con un ratón)
        if handle_deposito(self, mapa):
            # ya planeó siguiente movimiento o regreso a base
            pass

        # 10) Prioridad plato (interrumpe lo que sea)
        if prioridad_plato(self, mapa):
            pass

        # 11) Planear si no hay ruta
        planear_si_no_hay_ruta(self, mapa)

        # 12) Salvaguarda de energía
        salvaguarda_energia(self, mapa)

        # 13) Re-enfoque (solo si NO persigue; si persigue, mantener o volver a flujo)
        if not self.bebiendo and not self.jugando:
            if not self.persiguiendo:
                recalcular_si_conviene(self, mapa, VISION, RECALC_COOLDOWN_MS)
            else:
                mantener_persecucion_o_volver_flujo(self, mapa)

        # 14) Movimiento final de un paso
        if self.ruta and not self.bebiendo and not self.jugando:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)
        
        self.ultimo_tick = self._ticks()

    # Render delega a módulo original (sin cambios visuales)
    def dibujar(self, pantalla):
        dibujar_render(self, pantalla)
