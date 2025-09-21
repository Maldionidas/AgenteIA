import pygame
from config import *
# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base):
        self.mapa = mapa#matriz del mapa
        self.base = base#posicion de la base (1,1)

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                # Base
                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, BASE_COLOR, (x, y, TAM, TAM))

                # Muros
                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))

                # Pelota
                elif valor == CELDA_PELOTA: 
                    pygame.draw.circle(pantalla, (200, 200, 50),
                                       (x + TAM // 2, y + TAM // 2), TAM // 3)

                # Vacío
                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                # dibujar la celda
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)