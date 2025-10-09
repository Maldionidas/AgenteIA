# Agente/movimiento.py
from config import FILAS, COLS, CELDA_MURO, COSTOS, TAM, CELDA_ALFOMBRA, CELDA_AGUA
from .constants import SLOW_MS_ALFOMBRA, SLOW_MS_AGUA

def mover(agent, accion, mapa):
    df, dc = 0, 0
    if accion == "arriba":
        df = -1; agent.dir = "back"
    elif accion == "abajo":
        df = 1;  agent.dir = "front"
    elif accion == "izquierda":
        dc = -1; agent.dir = "left"
    elif accion == "derecha":
        dc = 1;  agent.dir = "right"

    nf = agent.fila + df
    nc = agent.col + dc
    if 0 <= nf < FILAS and 0 <= nc < COLS and mapa[nf][nc] != CELDA_MURO:
        agent.fila, agent.col = nf, nc
        celda = mapa[nf][nc]
        coste = COSTOS.get(celda, 1)
        if agent.energia.valor > 0:
            agent.energia.valor = max(0, agent.energia.valor - coste * agent.energia.costo_paso)
        # reset anti-retrigger al moverse
        agent._evitar_retrigger_estambre = False
        agent._evitar_retrigger_leche = False

        # Lentitud visual según celda pisada
        ahora = agent._ticks()
        if celda == CELDA_ALFOMBRA:
            agent._slow_until = ahora + SLOW_MS_ALFOMBRA
            agent._slow_reason = "alfombra"
        elif celda == CELDA_AGUA:
            agent._slow_until = ahora + SLOW_MS_AGUA
            agent._slow_reason = "agua"
        else:
            # sin lentitud
            agent._slow_until = 0
            agent._slow_reason = None
