import pygame
#Configuración inicial
TAM = 40 #tamaño de las celdas en px
FILAS, COLS = 20, 20 #filas y columnas
ANCHO, ALTO = COLS * TAM, FILAS * TAM #dimension del mapa


# Constantes de celdas
CELDA_VACIA = 0
CELDA_MURO = 1
CELDA_RATON = 2

# Colores de los objetos
VACIO = (200, 200, 200)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)
JUGADOR = (50, 100, 255)
CELDA_RATON = (100, 100, 100)
BASE_COLOR = (0, 0, 255)   # Azul para la base
DEPOSITO_COLOR = (0, 255, 0)


# Fuente para HUD
pygame.font.init()
FUENTE = pygame.font.SysFont("Arial", 24)
#casilla para recargar bombas
BASE = (1, 1)
DEPOSITO = (1, COLS-2)
VELOCIDAD = 4