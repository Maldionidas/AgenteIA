import pygame
from config import TAM, MAX_BOMBAS, CELDA_VACIA, JUGADOR

# --- Clase Jugador ---
class Jugador:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.x = col * TAM + TAM // 2
        self.y = fila * TAM + TAM // 2
        self.max_bombas = 3
        self.bombas_restantes = self.max_bombas
        #self.base = base

    def mover(self, teclas, mapa):
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            if mapa[self.fila - 1][self.col] == CELDA_VACIA:
                self.fila -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            if mapa[self.fila + 1][self.col] == CELDA_VACIA:
                self.fila += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            if mapa[self.fila][self.col - 1] == CELDA_VACIA:
                self.col -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            if mapa[self.fila][self.col + 1] == CELDA_VACIA:
                self.col += 1

        # Actualizar posición
        self.x = self.col * TAM + TAM // 2
        self.y = self.fila * TAM + TAM // 2
        
        
        #funcion para colocar las bombas
        '''
        def colocar_bomba(self, bombas, ahora):
            if self.bombas_restantes > 0:
                celda = (self.fila, self.col)
                if not any(b.celda == celda and not b.exploto for b in bombas):
                    bombas.append(Bomba(celda, ahora))
                    self.bombas_restantes -= 1
                    '''

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, JUGADOR, (self.x, self.y), TAM//2 - 6)