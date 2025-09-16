import pygame
from config import *
# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base):
        self.mapa = mapa
        self.base = base

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                if (fila, col) == self.base:
                    color = BASE_COLOR
                else:
                    color = VACIO if valor == CELDA_VACIA else MURO if valor == CELDA_MURO else DESTRUIBLE
                pygame.draw.rect(pantalla, color, (col*TAM, fila*TAM, TAM, TAM))
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)