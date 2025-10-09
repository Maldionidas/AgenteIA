# escenario_utils.py
import random
from config import FILAS, COLS, CELDA_VACIA, CELDA_RATON, CELDA_MURO, CELDA_COMIDA

def sincronizar_lista_con_mapa(esc):
    vivos = []
    for r in esc.ratones:
        if 0 <= r.fila < FILAS and 0 <= r.col < COLS and esc.mapa[r.fila][r.col] == CELDA_RATON:
            vivos.append(r)
    esc.ratones = vivos

def actualizar_ratones(esc):
    # Paso 1: liberar
    for r in esc.ratones:
        if esc.mapa[r.fila][r.col] == CELDA_RATON:
            esc.mapa[r.fila][r.col] = CELDA_VACIA

    # Paso 2: mover en orden aleatorio
    orden = list(esc.ratones)
    random.shuffle(orden)
    ocupadas = set()
    for r in orden:
        pos_antes = (r.fila, r.col)
        r.actualizar(esc.mapa, esc.gato_pos)
        pos_despues = (r.fila, r.col)
        if pos_despues in ocupadas:
            r.fila, r.col = pos_antes
            pos_despues = pos_antes
        ocupadas.add(pos_despues)

    # Paso 3: recolocar bandera
    for r in esc.ratones:
        if esc.mapa[r.fila][r.col] == CELDA_VACIA:
            esc.mapa[r.fila][r.col] = CELDA_RATON

def spawn_plato_si_toca(esc):
    import pygame
    ahora = pygame.time.get_ticks()
    if ahora - esc._last_food_spawn < esc.food_interval_ms:
        return
    esc._last_food_spawn = ahora
    candidatos = [(f, c) for f in range(FILAS) for c in range(COLS)
                  if esc.mapa[f][c] == CELDA_VACIA and (f, c) not in (esc.base, esc.deposito)]
    random.shuffle(candidatos)
    for f, c in candidatos:
        vecinos = [(f-1,c), (f+1,c), (f,c-1), (f,c+1)]
        accesible = any(0 <= nf < FILAS and 0 <= nc < COLS and esc.mapa[nf][nc] != CELDA_MURO for nf, nc in vecinos)
        if not accesible:
            continue
        esc.mapa[f][c] = CELDA_COMIDA
        esc._platos_colocados += 1
        break
