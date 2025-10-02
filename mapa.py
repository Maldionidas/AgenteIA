import random
from config import FILAS, COLS, CELDA_MURO, CELDA_VACIA, CELDA_RATON, CELDA_AGUA, CELDA_ALFOMBRA, CELDA_ESTAMBRE, BASE, DEPOSITO

def generar_mapa(muros_fijos=None, num_ratones=10, num_obstaculos=20, num_agua=10, num_alfombra=10, num_estambre=2):
    """Genera un mapa con muros, obstáculos aleatorios, ratones aleatorios y 2 bolas de estambre en celdas válidas."""
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

    # Posiciones libres básicas (evitar base y depósito)
    def libres_excluyendo(*excluir):
        excl = set(excluir)
        return [(f, c) for f in range(FILAS) for c in range(COLS)
                if mapa[f][c] == CELDA_VACIA and (f, c) not in excl]

    # Seleccionar posiciones de ratones
    libres = libres_excluyendo(BASE, DEPOSITO)
    pelotas = random.sample(libres, min(num_ratones, len(libres)))
    for f, c in pelotas:
        mapa[f][c] = CELDA_RATON

    # Recalcular libres para obstáculos (no base, no depósito, no ratones)
    libres = libres_excluyendo(BASE, DEPOSITO)
    obstaculos = random.sample(libres, min(num_obstaculos, len(libres)))
    for f, c in obstaculos:
        mapa[f][c] = CELDA_MURO
        
    # --- AGUA ---
    libres = libres_excluyendo(BASE, DEPOSITO)
    aguas = random.sample(libres, min(num_agua, len(libres)))
    for f, c in aguas:
        mapa[f][c] = CELDA_AGUA

    # --- ALFOMBRA ---
    libres = libres_excluyendo(BASE, DEPOSITO)
    alfombras = random.sample(libres, min(num_alfombra, len(libres)))
    for f, c in alfombras:
        mapa[f][c] = CELDA_ALFOMBRA

    # --- ESTAMBRE (2 bolas, lejos una de otra y fuera de agua/alfombra/base/depósito) ---
    def celdas_validas_estambre():
        return [(f, c) for f in range(FILAS) for c in range(COLS)
                if mapa[f][c] == CELDA_VACIA and (f, c) not in (BASE, DEPOSITO)]

    candidatos = celdas_validas_estambre()
    random.shuffle(candidatos)

    estambres_colocados = 0
    colocados = []
    MIN_DIST = 6  # "retiradas una de otra"
    for f, c in candidatos:
        if estambres_colocados >= num_estambre:
            break
        # Deben estar lejos entre sí
        if any(abs(f - ef) + abs(c - ec) < MIN_DIST for (ef, ec) in colocados):
            continue
        mapa[f][c] = CELDA_ESTAMBRE
        colocados.append((f, c))
        estambres_colocados += 1

    return mapa
