# Agente/percepcion.py
from config import FILAS, COLS, CELDA_RATON
from .busquedaRuta import dijkstra

def raton_mas_cercano(agent, mapa):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    mejor = None
    mejor_len = None
    for p in ratones:
        r = dijkstra(mapa, (agent.fila, agent.col), [p])
        if r:
            if mejor is None or len(r) < mejor_len:
                mejor = p
                mejor_len = len(r)
    return mejor

def raton_visible_y_ruta(agent, mapa, VISION):
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    mejor = None
    mejor_ruta = None
    for p in ratones:
        r = dijkstra(mapa, (agent.fila, agent.col), [p]) or []
        if r and len(r) <= VISION:
            if mejor_ruta is None or len(r) < len(mejor_ruta):
                mejor, mejor_ruta = p, r
    return mejor, (mejor_ruta or [])

def objetivo_visible_por_celda(agent, mapa, celda_obj, VISION):
    candidatos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == celda_obj]
    mejor = None
    mejor_ruta = None
    for p in candidatos:
        r = dijkstra(mapa, (agent.fila, agent.col), [p]) or []
        if r and len(r) <= VISION:
            if mejor_ruta is None or len(r) < len(mejor_ruta):
                mejor, mejor_ruta = p, r
    return mejor, mejor_ruta
