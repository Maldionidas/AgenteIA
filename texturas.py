# texturas.py
import pygame
from config import TAM

TEXTURAS_PATHS = {
    "cama": "personajes/cama.png",
    "deposito_0": "personajes/deposito_0.png",
    "deposito_1": "personajes/deposito_1.png",
    "deposito_2": "personajes/deposito_2.png",
    "deposito_3": "personajes/deposito_3.png",
    "deposito_4": "personajes/deposito_4.png",
    "charco": "personajes/charco.png",
    "bola": "personajes/bola.png",
    "plato": "personajes/plato.png",
}

def cargar_img(ruta, tam=TAM):
    img = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(img, (tam, tam))
