import pygame
from config import *
# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base, deposito):
        self.mapa = mapa#matriz del mapa
        self.base = base#posicion de la base (1,1)
        self.deposito = deposito

        original = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)  # más pequeño que la celda
        self.raton_img = pygame.transform.scale(original, (raton_size, raton_size))

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                # Base
                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, BASE_COLOR, (x, y, TAM, TAM))

                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, DEPOSITO_COLOR, (x, y, TAM, TAM))

                # Muros
                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))

                # Pelota
                elif valor == CELDA_PELOTA: 
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))

                # Vacío
                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                # dibujar la celda
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)