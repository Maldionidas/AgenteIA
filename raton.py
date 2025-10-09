# raton.py
import random
import pygame
from config import FILAS, COLS, TAM, CELDA_VACIA, CELDA_AGUA, CELDA_ALFOMBRA, CELDA_MURO, BASE, DEPOSITO

class Raton:
    """
    Raton móvil en la grilla.
    - Mantiene movimiento aleatorio cada tick_ms.
    - Si ve al gato (dist. Manhattan <= VISION), intenta huir eligiendo
      la celda vecina que maximiza la distancia Manhattan al gato.
    """
    VISION = 12  # radio de visión del ratón (Manhattan). Ajusta si quieres.

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

    @staticmethod
    def _dist_manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def actualizar(self, mapa, gato_pos=None):
        """
        Si gato_pos está cerca (<= VISION), huye.
        Si no, comportamiento aleatorio como antes.
        """
        ahora = pygame.time.get_ticks()
        if ahora - self._ultimo_tick < self.tick_ms:
            return  # aún no toca moverse
        self._ultimo_tick = ahora

        # Opciones de movimiento: SOLO VACÍA y que NO sean base ni depósito
        opciones = []
        for nf, nc in self._celdas_vecinas(mapa):
            if (nf, nc) == BASE or (nf, nc) == DEPOSITO:
                continue
            if mapa[nf][nc] == CELDA_VACIA:
                opciones.append((nf, nc))

        if not opciones:
            return  # sin movimientos válidos

        # --- HUIDA si el gato está en visión (distancia Manhattan)
        if gato_pos is not None:
            dist_actual = self._dist_manhattan((self.fila, self.col), gato_pos)
            if dist_actual <= self.VISION:
                # elegir la(s) opción(es) que maximicen la distancia al gato
                mejor_dist = -1
                candidatos = []
                for pos in opciones:
                    d = self._dist_manhattan(pos, gato_pos)
                    if d > mejor_dist:
                        mejor_dist = d
                        candidatos = [pos]
                    elif d == mejor_dist:
                        candidatos.append(pos)

                # si hay candidatos, elige uno al azar entre los mejores
                if candidatos:
                    nf, nc = random.choice(candidatos)
                    mapa[self.fila][self.col] = CELDA_VACIA
                    self.fila, self.col = nf, nc
                    # El valor de "ratón" en el mapa lo gestiona Escenario al final del update.
                    return

        # --- Si no vio al gato o no pudo alejarse más, movimiento aleatorio (comportamiento actual)
        nf, nc = random.choice(opciones)
        mapa[self.fila][self.col] = CELDA_VACIA
        self.fila, self.col = nf, nc
        # El valor de "ratón" en el mapa lo gestiona Escenario al final del update.
