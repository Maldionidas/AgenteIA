import random
from config import FILAS, COLS, CELDA_MURO, CELDA_VACIA, CELDA_RATON, BASE, DEPOSITO

def generar_mapa(muros_fijos=None, num_ratones=10, num_obstaculos=20):
    """Genera un mapa con muros, obstáculos aleatorios y ratones aleatorios en celdas libres."""
    mapa = [[CELDA_VACIA for _ in range(COLS)] for _ in range(FILAS)]

    # Bordes del mapa, delimitador
    for f in range(FILAS):
        for c in range(COLS):
            if f == 0 or f == FILAS-1 or c == 0 or c == COLS-1:
                mapa[f][c] = CELDA_MURO

    # Agregar muros fijos personalizados
    if muros_fijos:
        for f, c in muros_fijos:
            if 0 <= f < FILAS and 0 <= c < COLS:
                mapa[f][c] = CELDA_MURO

    # Buscar posiciones libres para ratones (evitar base y depósito)
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if mapa[f][c] == CELDA_VACIA and (f, c) not in [BASE, DEPOSITO]]

    # Seleccionar posiciones de ratones
    pelotas = random.sample(libres, min(num_ratones, len(libres)))
    for f, c in pelotas:
        mapa[f][c] = CELDA_RATON

    # Recalcular libres para obstáculos (no base, no depósito, no ratones)
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if mapa[f][c] == CELDA_VACIA and (f, c) not in [BASE, DEPOSITO]]

    # Seleccionar obstáculos
    obstaculos = random.sample(libres, min(num_obstaculos, len(libres)))
    for f, c in obstaculos:
        mapa[f][c] = CELDA_MURO

    return mapa
