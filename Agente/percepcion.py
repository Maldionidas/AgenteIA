# Agente/percepcion.py
from config import FILAS, COLS, CELDA_RATON
from .geneticAlg import genetic_shortest, genetic_cost


def _manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def raton_mas_cercano(agent, mapa):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    mejor = None
    mejor_cost = None
#    mejor_ruta = None
    for p in ratones:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and (mejor_cost is None or cost < mejor_cost):
            mejor, mejor_cost = p, cost
    return mejor

def raton_visible_y_ruta(agent, mapa, VISION):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    candidatos = [p for p in ratones if _manhattan((agent.fila, agent.col), p) <= VISION]
    mejor, mejor_cost, mejor_ruta = None, None, None
    for p in candidatos:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and (mejor_cost is None or cost < mejor_cost):
            mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, (mejor_ruta or [])
''' mejor = None
    mejor_cost = None
    mejor_ruta = None
    for p in ratones:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and len(ruta) <= VISION:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, (mejor_ruta or [])'''

def objetivo_visible_por_celda(agent, mapa, celda_obj, VISION):
    candidatos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == celda_obj]
    dentro = [p for p in candidatos if _manhattan((agent.fila, agent.col), p) <= VISION]
    mejor, mejor_cost, mejor_ruta = None, None, None
    for p in dentro:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and (mejor_cost is None or cost < mejor_cost):
            mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, (mejor_ruta or [])
'''    mejor = None
    mejor_cost = None
    mejor_ruta = None
    for p in candidatos:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and len(ruta) <= VISION:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, mejor_ruta
'''