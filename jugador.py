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
    #funcion para mover al jugador
    #utiliza wasd, se mueve mediante coordenadas, va agregrando o restando a fila y columna
    def mover(self, teclas, mapa):
        if teclas[pygame.K_w]:
            if mapa[self.fila - 1][self.col] == CELDA_VACIA:
                self.fila -= 1
        if teclas[pygame.K_s]:
            if mapa[self.fila + 1][self.col] == CELDA_VACIA:
                self.fila += 1
        if teclas[pygame.K_a]:
            if mapa[self.fila][self.col - 1] == CELDA_VACIA:
                self.col -= 1
        if teclas[pygame.K_d]:
            if mapa[self.fila][self.col + 1] == CELDA_VACIA:
                self.col += 1

        # Actualizar posición
        self.x = self.col * TAM + TAM // 2
        self.y = self.fila * TAM + TAM // 2
        
    #funcion para dibujar al jugador
    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, JUGADOR, (self.x, self.y), TAM//2 - 6)
