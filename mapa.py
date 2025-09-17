import random
from config import FILAS, COLS, CELDA_MURO, CELDA_DESTRUIBLE, CELDA_VACIA

def generar_mapa():
    mapa = []
    for fila in range(FILAS):
        fila_data = []
        for col in range(COLS):
            #genera margen de muros y muros interiores no destruibles
            if fila == 0 or fila == FILAS-1 or col == 0 or col == COLS-1:
                fila_data.append(CELDA_MURO)
                #muros interiores no destruibles, intercambiando fila y columna pares
            elif fila % 2 == 0 and col % 2 == 0:
                fila_data.append(CELDA_MURO)
            else:
                #genera muros destruibles aleatoriamente
                fila_data.append(CELDA_DESTRUIBLE if random.random() < 0.3 else CELDA_VACIA)
        mapa.append(fila_data)

    # Zona inicial limpia
    mapa[1][1] = CELDA_VACIA
    mapa[1][2] = CELDA_VACIA
    mapa[2][1] = CELDA_VACIA
    return mapa

mapa = generar_mapa()