# escenario.py
import pygame
import random
from config import *
from raton import Raton
from texturas import TEXTURAS_PATHS, cargar_img
from escenario_utils import sincronizar_lista_con_mapa, actualizar_ratones, spawn_plato_si_toca

class Escenario:
    def __init__(self, mapa, base, deposito):
        self.mapa = mapa
        self.base = base
        self.deposito = deposito

        self.entregados_base = 0
        self.entregados_deposito = 0
        self.gato_pos = None

        original = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(original, (raton_size, raton_size))

        self.img_cama = cargar_img(TEXTURAS_PATHS["cama"])
        self.img_charco = cargar_img(TEXTURAS_PATHS["charco"])
        self.img_estambre = cargar_img(TEXTURAS_PATHS["bola"])
        self.img_plato = cargar_img(TEXTURAS_PATHS["plato"])
        self.img_cajas = [
            cargar_img(TEXTURAS_PATHS["deposito_0"]),
            cargar_img(TEXTURAS_PATHS["deposito_1"]),
            cargar_img(TEXTURAS_PATHS["deposito_2"]),
            cargar_img(TEXTURAS_PATHS["deposito_3"]),
            cargar_img(TEXTURAS_PATHS["deposito_4"]),
        ]

        self.ratones = []
        for f in range(FILAS):
            for c in range(COLS):
                if self.mapa[f][c] == CELDA_RATON:
                    self.ratones.append(Raton(f, c, tick_ms=400))

        self.food_interval_ms = 120_000
        self._last_food_spawn = pygame.time.get_ticks()
        self._platos_colocados = 0

    def set_gato_pos(self, fila, col):
        self.gato_pos = (fila, col)

    def dibujar(self, pantalla):
        # Misma secuencia de actualizaciones que antes:
        sincronizar_lista_con_mapa(self)
        actualizar_ratones(self)
        spawn_plato_si_toca(self)

        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_cama, (x, y))

                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    idx = self.entregados_deposito
                    if idx > 4:
                        idx = 4
                    pantalla.blit(self.img_cajas[idx], (x, y))

                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))

                elif valor == CELDA_RATON:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))

                elif valor == CELDA_AGUA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_charco, (x, y))

                elif valor == CELDA_ALFOMBRA:
                    pygame.draw.rect(pantalla, (255, 200, 150), (x, y, TAM, TAM))

                elif valor == CELDA_ESTAMBRE:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_estambre, (x, y))

                elif valor == CELDA_COMIDA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_plato, (x, y))

                elif valor == CELDA_VACIA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
