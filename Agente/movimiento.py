# Agente/movimiento.py
from config import FILAS, COLS, CELDA_MURO, COSTOS, TAM

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
        coste = COSTOS.get(mapa[nf][nc], 1)
        if agent.energia.valor > 0:
            agent.energia.valor = max(0, agent.energia.valor - coste * agent.energia.costo_paso)
        # reset anti-retrigger al moverse
        agent._evitar_retrigger_estambre = False
        agent._evitar_retrigger_leche = False
