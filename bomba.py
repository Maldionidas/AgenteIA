import pygame
from config import *
#Clase Bomba
class Bomba:
    def __init__(self, celda, t_colocada):
        self.celda = celda
        self.t_colocada = t_colocada
        self.exploto = False
        self.t_explosion = None
        self.llamas = []

    def deberia_explotar(self, ahora):
        return (not self.exploto) and (ahora - self.t_colocada >= FUSIBLE_MS)

    def explotar(self, mapa):
        self.exploto = True
        self.t_explosion = pygame.time.get_ticks()
        f0, c0 = self.celda
        self.llamas = [(f0, c0)]
        for df, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            for paso in range(1, ALCANCE_LLAMA+1):
                f = f0 + df*paso
                c = c0 + dc*paso
                if not (0 <= f < FILAS and 0 <= c < COLS):
                    break
                if mapa[f][c] == CELDA_MURO:
                    break
                self.llamas.append((f, c))
                if mapa[f][c] == CELDA_DESTRUIBLE:
                    mapa[f][c] = CELDA_VACIA
                    break

    def llamas_activas(self, ahora):
        return self.exploto and (ahora - self.t_explosion <= DURACION_LLAMA_MS)

    def dibujar(self, pantalla, ahora):
        f, c = self.celda
        if not self.exploto:
            pygame.draw.circle(pantalla, BOMBA_COLOR,
                               (c*TAM + TAM//2, f*TAM + TAM//2), TAM//3)
        elif self.llamas_activas(ahora):
            for f, c in self.llamas:
                pygame.draw.rect(pantalla, LLAMA_COLOR,
                                 (c*TAM, f*TAM, TAM, TAM))