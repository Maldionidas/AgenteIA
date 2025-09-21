import pygame
from config import *

class Gato:
    def __init__(self, fila, col):
        # Cargar imágenes del gato
        self.images = {
            "front": pygame.image.load("cat_front.png"),
            "back": pygame.image.load("cat_back.png"),
            "left": pygame.image.load("cat_left.png"),
            "right": pygame.image.load("cat_right.png")
        }
        self.dir = "front"   # dirección inicial
        self.fila = fila
        self.col = col

        # Escalar al tamaño de celda
        for k, img in self.images.items():
            self.images[k] = pygame.transform.scale(img, (TAM, TAM))

    def mover(self, dx, dy):
        self.fila += dy
        self.col += dx
        # cambiar sprite según dirección
        if dx > 0: self.dir = "right"
        elif dx < 0: self.dir = "left"
        elif dy > 0: self.dir = "down"
        elif dy < 0: self.dir = "up"

    def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        if self.dir == "down": pantalla.blit(self.images["front"], (x, y))
        elif self.dir == "up": pantalla.blit(self.images["back"], (x, y))
        elif self.dir == "left": pantalla.blit(self.images["left"], (x, y))
        elif self.dir == "right": pantalla.blit(self.images["right"], (x, y))
        else: pantalla.blit(self.images["front"], (x, y))
