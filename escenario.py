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
                #si es la base, dibujarla de otro color
                if (fila, col) == self.base:
                    color = BASE_COLOR
                else:
                    # determinar color según el valor de la celda
                    if valor == CELDA_VACIA:
                        color = VACIO
                    elif valor == CELDA_MURO:
                        color = MURO
                    else:
                        color = DESTRUIBLE
                        #si es destructible, dibujar un rectángulo marrón
                # dibujar la celda
                pygame.draw.rect(pantalla, color, (col*TAM, fila*TAM, TAM, TAM))
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)