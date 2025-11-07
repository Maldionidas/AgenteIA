# Agente/AgenteIA.py
import pygame
from config import TAM
from .energia import Energia
from .render import dibujar as dibujar_render
from .constants import (VISION, COSTO_SPRINT, COSTO_NORMAL, RECALC_COOLDOWN_MS, JUEGO_MS, BEBER_MS)
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
    planear_si_no_hay_ruta,
    salvaguarda_energia,                     
    mantener_persecucion_o_volver_flujo,     
    prioridad_plato_fuerte,
)

from .movimiento import mover as mover_fn

class AgenteIA:
    def __init__(self, fila, col, base,mapa, deposito, color=(200, 50, 50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3
        self.mapa = mapa

        self.ruta = []
        self.objetivo = None
        self.cargando = False
        self.fue_deposito = False
        self.contador_deposito = 0
        self.recolectadas = 0
        self.bebiendo = False
        self.jugando = False
        # --- timers/flags que usa states.py ---
        self.inicio_juego = 0
        self.tiempo_juego_ms = JUEGO_MS
        self._ultimo_tick_juego = pygame.time.get_ticks()
        self.inicio_bebida = 0
        self.tiempo_bebida_ms = BEBER_MS
        self._evitar_retrigger_estambre = False
        self._evitar_retrigger_leche = False
        self.cooldown_estambre_hasta = 0
        self.ignorar_estambre_hasta_base = False
        self._evitar_descanso_hasta = 0

        self.animando = False
        self.inicio_animacion = 0
        self.tiempo_animacion = 1000
        self.estado = "Idle"

        self.font = pygame.font.SysFont(None, max(16, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        self.energia = Energia(energia_max=300, recarga_por_segundo=40, costo_paso=1)

        self.images = {
            "front": pygame.transform.scale(pygame.image.load("personajes/cat_front.png").convert_alpha(), (TAM, TAM)),
            "back":  pygame.transform.scale(pygame.image.load("personajes/cat_back.png").convert_alpha(),  (TAM, TAM)),
            "left":  pygame.transform.scale(pygame.image.load("personajes/cat_left.png").convert_alpha(),  (TAM, TAM)),
            "right": pygame.transform.scale(pygame.image.load("personajes/cat_right.png").convert_alpha(), (TAM, TAM)),
        }
        self.dir = "front"

        raton = pygame.image.load("personajes/raton.png").convert_alpha()
        rs = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(raton, (rs, rs))

        self._ultimo_recalculo = 0
        self.ultimo_tick = pygame.time.get_ticks()
        self.recargando = False
        self.persiguiendo = False
        self.yendo_por_leche = False

        # slow visual
        self._slow_until = 0
        self._slow_reason = None

    def _ticks(self):
        return pygame.time.get_ticks()

    def mover(self, accion, mapa):
        mover_fn(self, accion, mapa)

    def actualizar(self, mapa):
        ensure_runtime_flags(self)
        self.energia.costo_paso = int(COSTO_SPRINT if self.persiguiendo else COSTO_NORMAL)

        # Prioridad absoluta: plato
        prioridad_plato_fuerte(self, mapa)

        # Estados “bloqueantes”
        if handle_bebiendo(self, mapa):
            return
        if handle_jugando(self, mapa):
            return
        if end_pick_animation_if_done(self, mapa):
            if self.animando:
                return

        # Sin energía / recarga (no si va por leche)
        if not self.yendo_por_leche:
            if handle_sin_energia(self, mapa):
                return
            if handle_en_base_y_recarga(self, mapa):
                return
        self.ultimo_tick = self._ticks()

        # Post-depósito: conteo
        if not self.cargando and self.fue_deposito and (self.fila, self.col) == self.base:
            self.recolectadas += 1
            self.fue_deposito = False
            self.objetivo = None
            self.ruta = []

        # Interacciones en celda
        if step_on_raton(self, mapa):
            return
        if step_on_plato(self, mapa):
            return
        if step_on_estambre(self, mapa):
            return

        # Depósito
        if handle_deposito(self, mapa):
            pass

        # Planificación y salvaguarda
        planear_si_no_hay_ruta(self, mapa)
        if not self.yendo_por_leche:
            salvaguarda_energia(self, mapa)

        # Re-enfoque / persecución
        if not self.bebiendo and not self.jugando:
            if not self.persiguiendo:
                recalcular_si_conviene(self, mapa, VISION, RECALC_COOLDOWN_MS)
            else:
                mantener_persecucion_o_volver_flujo(self, mapa)

        # Lentitud visual: pausar paso si aún bajo efecto
        ahora = self._ticks()
        if ahora < getattr(self, "_slow_until", 0):
            if self._slow_reason == "alfombra":
                self.estado = "Avanzando (alfombra)"
            elif self._slow_reason == "agua":
                self.estado = "Avanzando (agua)"
            return  # no se mueve este frame

        # Movimiento de un paso
        if self.ruta and not self.bebiendo and not self.jugando:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

    def dibujar(self, pantalla):
        dibujar_render(self, pantalla)