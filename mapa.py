import random
from config import FILAS, COLS, CELDA_MURO, CELDA_VACIA, CELDA_PELOTA

import random



def generar_mapa(muros_fijos=None,num_ratones=None):
    """Genera un mapa con muros fijos y pelotas aleatorias."""
    
    mapa = [[CELDA_VACIA for _ in range(COLS)] for _ in range(FILAS)]

    # Bordes automáticos
    for f in range(FILAS):
        for c in range(COLS):
            if f == 0 or f == FILAS-1 or c == 0 or c == COLS-1:
                mapa[f][c] = CELDA_MURO

    # Agregar muros fijos personalizados
    if muros_fijos:
        for f, c in muros_fijos:
            if 0 <= f < FILAS and 0 <= c < COLS:
                mapa[f][c] = CELDA_MURO

    # Buscar todas las posiciones vacías
    libres = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_VACIA]

    # Seleccionar posiciones al azar para los ratones
    pelotas = random.sample(libres, min(num_ratones, len(libres)))
    for f, c in pelotas:
        mapa[f][c] = CELDA_PELOTA

        # Agregar pelotas personalizadas
        #if pelotas:
        #    for f, c in pelotas:
        #        if 0 <= f < FILAS and 0 <= c < COLS:
        #            mapa[f][c] = CELDA_PELOTA
        
        
    return mapa
