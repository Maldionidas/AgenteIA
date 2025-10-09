import random
import math
from config import (FILAS, COLS, CELDA_VACIA, CELDA_MURO, CELDA_AGUA, CELDA_ALFOMBRA,
                    CELDA_ESTAMBRE, CELDA_RATON, BASE, DEPOSITO)

def _vecinos4(f, c):
    return [(f-1,c), (f+1,c), (f,c-1), (f,c+1)]

def _dentro(f, c):
    return 0 <= f < FILAS and 0 <= c < COLS

def _colocar_clusters(mapa, celda_tipo, cantidad_celdas, tam_min=1, tam_max=5, intentos=500):
    restantes = cantidad_celdas
    guardas = {(BASE[0], BASE[1]), (DEPOSITO[0], DEPOSITO[1])}

    while restantes > 0 and intentos > 0:
        intentos -= 1
        f = random.randrange(FILAS)
        c = random.randrange(COLS)
        if (f, c) in guardas or mapa[f][c] != CELDA_VACIA:
            continue

        tam = random.randint(tam_min, tam_max)
        cluster = [(f, c)]
        usados = {(f, c)}
        cola = [(f, c)]
        while cola and len(cluster) < tam:
            cf, cc = cola.pop(0)
            vecinos = _vecinos4(cf, cc)
            random.shuffle(vecinos)
            for nf, nc in vecinos:
                if not _dentro(nf, nc):
                    continue
                if (nf, nc) in usados:
                    continue
                if (nf, nc) in guardas:
                    continue
                if mapa[nf][nc] != CELDA_VACIA:
                    continue
                if random.random() < 0.7:
                    cluster.append((nf, nc))
                    usados.add((nf, nc))
                    cola.append((nf, nc))
                    if len(cluster) >= tam:
                        break

        for cf, cc in cluster:
            if restantes <= 0:
                break
            mapa[cf][cc] = celda_tipo
            restantes -= 1

def _dist_manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _colocar_separado(mapa, celda_tipo, cantidad, min_dist=7, avoid=set(), max_intentos=4000):
    """
    Coloca 'cantidad' celdas de tipo 'celda_tipo' garantizando una distancia mínima
    de 'min_dist' (Manhattan) entre cada par colocado. Si no se logra, relaja
    progresivamente la distancia.
    """
    colocados = []
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if mapa[f][c] == CELDA_VACIA and (f, c) not in avoid]
    random.shuffle(libres)

    intento = 0
    d = min_dist
    while len(colocados) < cantidad and intento < max_intentos:
        intento += 1
        if not libres:
            break
        f, c = libres.pop()
        pos = (f, c)
        ok = True
        for p in colocados:
            if _dist_manhattan(p, pos) < d:
                ok = False
                break
        if ok:
            mapa[f][c] = celda_tipo
            colocados.append(pos)
        # Si nos atoramos mucho, relajamos la distancia
        if intento % 500 == 0 and d > 3:
            d -= 1
    return colocados

def _colocar_al_azar(mapa, celda_tipo, cantidad, avoid=set()):
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if mapa[f][c] == CELDA_VACIA and (f, c) not in avoid]
    random.shuffle(libres)
    puestos = 0
    for f, c in libres:
        if puestos >= cantidad:
            break
        mapa[f][c] = celda_tipo
        puestos += 1

def generar_mapa(num_ratones=10, num_obstaculos=20, num_agua=8, num_alfombra=10, num_estambre=4):
    mapa = [[CELDA_VACIA for _ in range(COLS)] for _ in range(FILAS)]

    # base/deposito libres
    mapa[BASE[0]][BASE[1]] = CELDA_VACIA
    mapa[DEPOSITO[0]][DEPOSITO[1]] = CELDA_VACIA

    # muros sueltos
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if (f, c) not in (BASE, DEPOSITO)]
    random.shuffle(libres)
    for i in range(min(num_obstaculos, len(libres))):
        f, c = libres[i]
        mapa[f][c] = CELDA_MURO

    # clusters de agua y alfombra
    _colocar_clusters(mapa, CELDA_AGUA, num_agua, tam_min=1, tam_max=5)
    _colocar_clusters(mapa, CELDA_ALFOMBRA, num_alfombra, tam_min=1, tam_max=5)

    # ESTAMBRES RETIRADOS (min distancia Manhattan 7; relax si falta espacio)
    _colocar_separado(mapa, CELDA_ESTAMBRE, num_estambre, min_dist=7,
                      avoid={(BASE[0], BASE[1]), (DEPOSITO[0], DEPOSITO[1])})

    # ratones
    libres = [(f, c) for f in range(FILAS) for c in range(COLS)
              if mapa[f][c] == CELDA_VACIA and (f, c) not in (BASE, DEPOSITO)]
    random.shuffle(libres)
    for i in range(min(num_ratones, len(libres))):
        f, c = libres[i]
        mapa[f][c] = CELDA_RATON

    # garantizar base y depósito libres
    mapa[BASE[0]][BASE[1]] = CELDA_VACIA
    mapa[DEPOSITO[0]][DEPOSITO[1]] = CELDA_VACIA

    return mapa
