# raton.py
import random
import pygame
from config import FILAS, COLS, TAM, CELDA_VACIA, CELDA_AGUA, CELDA_ALFOMBRA, CELDA_MURO, BASE, DEPOSITO

class Raton:
    """
    Raton móvil en la grilla.
    - Se mueve a intervalos, una celda por paso.
    - Solo entra a celdas VACÍAS (con eso automáticamente evita agua, alfombra y muros).
    - No entra a BASE ni DEPOSITO (para evitar dibujado raro).
    """
    def __init__(self, fila, col, tick_ms=400):
        self.fila = fila
        self.col = col
        self.tick_ms = tick_ms
        self._ultimo_tick = pygame.time.get_ticks()

    def _celdas_vecinas(self, mapa):
        for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nf, nc = self.fila + df, self.col + dc
            if 0 <= nf < FILAS and 0 <= nc < COLS:
                yield nf, nc

    def actualizar(self, mapa):
        ahora = pygame.time.get_ticks()
        if ahora - self._ultimo_tick < self.tick_ms:
            return  # aún no toca moverse
        self._ultimo_tick = ahora

        # Opciones de movimiento: SOLO CELDA_VACIA y que NO sean base ni depósito
        opciones = []
        for nf, nc in self._celdas_vecinas(mapa):
            if (nf, nc) == BASE or (nf, nc) == DEPOSITO:
                continue
            if mapa[nf][nc] == CELDA_VACIA:
                opciones.append((nf, nc))

        if not opciones:
            return  # no hay a dónde moverse

        nf, nc = random.choice(opciones)
        # Liberar celda actual y ocupar la nueva
        mapa[self.fila][self.col] = CELDA_VACIA
        self.fila, self.col = nf, nc
        # El valor de "ratón" en el mapa lo gestiona Escenario al final del update.
