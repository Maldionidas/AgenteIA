import random
import pygame
from config import ANCHO, ALTO, TAM
from bomba import Bomba

COOL_DOWN_BOMBA = 2000  # frames de espera entre bombas

class AgenteIA:
    def __init__(self, fila, col, velocidad=1, color=(200, 50, 50)):
        self.fila = fila
        self.col = col
        self.velocidad = velocidad
        self.color = color
        self.radio = TAM//3
        self.direccion = random.choice(["arriba", "abajo", "izquierda", "derecha"])
        self.cooldown_bomba = 0  # para controlar que no ponga infinitas bombas
        
        self.contador = 0
        self.tiempo_cambio = 15

    def decidir(self):
        self.contador += 1
        if self.contador >= self.tiempo_cambio:
            self.direccion = random.choice(["arriba", "abajo", "izquierda", "derecha"])
            self.contador = 0
        return self.direccion
    
    def colocar_bomba(self, ahora, bombas):
        # Solo colocar bomba si ha pasado el cooldown
        if ahora - self.cooldown_bomba >= COOL_DOWN_BOMBA:
            celda = (self.fila, self.col)
            # Evitar duplicar bombas en la misma celda
            if not any(b.celda == celda and not b.exploto for b in bombas):
                bombas.append(Bomba(celda, ahora))
                self.cooldown_bomba = ahora


    def mover(self, accion, mapa):
        if accion == "arriba" and self.fila > 0 and mapa[self.fila-1][self.col] == 0:
            self.fila -= 1
        elif accion == "abajo" and self.fila < len(mapa)-1 and mapa[self.fila+1][self.col] == 0:
            self.fila += 1
        elif accion == "izquierda" and self.col > 0 and mapa[self.fila][self.col-1] == 0:
            self.col -= 1
        elif accion == "derecha" and self.col < len(mapa[0])-1 and mapa[self.fila][self.col+1] == 0:
            self.col += 1
        

    def dibujar(self, pantalla):
        x = self.col * TAM + TAM//2
        y = self.fila * TAM + TAM//2
        pygame.draw.circle(pantalla, self.color, (x, y), self.radio)
