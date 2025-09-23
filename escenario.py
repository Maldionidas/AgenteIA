import pygame
from config import *

# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base, deposito):
        self.mapa = mapa
        self.base = base
        self.deposito = deposito

        # contadores visibles independientes
        self.entregados_base = 0
        self.entregados_deposito = 0

        original = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(original, (raton_size, raton_size))

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, BASE_COLOR, (x, y, TAM, TAM))
                    # Dibuja ratones contabilizados en BASE
                    #self._dibujar_stack(pantalla, x, y, self.entregados_base)

                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, DEPOSITO_COLOR, (x, y, TAM, TAM))
                    # Dibuja ratones depositados (inmediato al pisar depósito)
                    self._dibujar_stack(pantalla, x, y, self.entregados_deposito)

                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))

                elif valor == CELDA_PELOTA:
                    pygame.draw.rect(pantalla, CELDA_PELOTA, (x, y, TAM, TAM))
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))

                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

    def _dibujar_stack(self, pantalla, x, y, n):
        """Dibuja n ratones en una retícula 2x2 (hasta 4)."""
        if n <= 0:
            return

        img_w, img_h = self.raton_img.get_size()

        # ligerito a la derecha y abajo
        dx = 2
        dy = 5

        offsets = [
            (TAM*0.15 + dx, TAM*0.15 + dy),  # arriba-izq
            (TAM*0.55 + dx, TAM*0.15 + dy),  # arriba-der
            (TAM*0.15 + dx, TAM*0.55 + dy),  # abajo-izq
            (TAM*0.55 + dx, TAM*0.55 + dy),  # abajo-der
        ]

        for i in range(min(n, 4)):
            ox, oy = offsets[i]
            pantalla.blit(self.raton_img, (x + ox - img_w/2, y + oy - img_h/2))
