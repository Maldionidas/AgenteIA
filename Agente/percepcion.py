# Agente/percepcion.py
from config import FILAS, COLS, CELDA_RATON
from .busquedaRuta import dijkstra, dijkstra_con_costo

def raton_mas_cercano(agent, mapa):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    mejor = None
    mejor_cost = None
    mejor_ruta = None
    for p in ratones:
        ruta, cost = dijkstra_con_costo(mapa, (agent.fila, agent.col), [p])
        if ruta:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor

def raton_visible_y_ruta(agent, mapa, VISION):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    mejor = None
    mejor_cost = None
    mejor_ruta = None
    for p in ratones:
        ruta, cost = dijkstra_con_costo(mapa, (agent.fila, agent.col), [p])
        if ruta and len(ruta) <= VISION:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, (mejor_ruta or [])

def objetivo_visible_por_celda(agent, mapa, celda_obj, VISION):
    candidatos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == celda_obj]
    mejor = None
    mejor_cost = None
    mejor_ruta = None
    for p in candidatos:
        ruta, cost = dijkstra_con_costo(mapa, (agent.fila, agent.col), [p])
        if ruta and len(ruta) <= VISION:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_cost, mejor_ruta = p, cost, ruta
    return mejor, mejor_ruta
