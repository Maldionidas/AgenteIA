import pygame
#Configuración inicial
TAM = 50 #tamaño de las celdas en px
FILAS, COLS = 11, 13 #filas y columnas
ANCHO, ALTO = COLS * TAM, FILAS * TAM #dimension del mapa


# Constantes de celdas
CELDA_VACIA = 0
CELDA_MURO = 1
CELDA_DESTRUIBLE = 2

# Colores de los objetos
VACIO = (200, 200, 200)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)
JUGADOR = (50, 100, 255)
BOMBA_COLOR = (0, 0, 0)   # negro para la bomba
LLAMA_COLOR = (255, 180, 0)  # naranja para la explosión
BASE_COLOR = (0, 0, 255)   # Azul para la base

# Bombas
FUSIBLE_MS = 1800
DURACION_LLAMA_MS = 350
ALCANCE_LLAMA = 1
MAX_BOMBAS = 3

# Fuente para HUD
pygame.font.init()
FUENTE = pygame.font.SysFont("Arial", 24)
#casilla para recargar bombas
BASE = (1, 1)
