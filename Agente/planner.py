# Agente/planner.py
from config import FILAS, COLS, CELDA_RATON
from .geneticAlg import genetic_shortest, genetic_cost, genetic_route
from .percepcion import raton_visible_y_ruta

def _ruta_hacia(agent, mapa, destino):
    agent.objetivo = destino
    agent.ruta = genetic_route(mapa, (agent.fila, agent.col), destino,
                               mode="HUNT",
                               energia_restante=agent.energia.valor,
                               cargando=False) or []

def recalcular_si_conviene(agent, mapa, VISION, cooldown_ms):
    if agent.cargando or agent.animando or agent.fue_deposito:
        return
    if not agent.ruta:
        return

    ahora = agent._ticks()
    if ahora - agent._ultimo_recalculo < cooldown_ms:
        return
    agent._ultimo_recalculo = ahora

    if agent.objetivo is None or agent.objetivo[0] < 0 or agent.objetivo[1] < 0:
        destino, ruta_vis = raton_visible_y_ruta(agent, mapa, VISION)
        if destino:
            _ruta_hacia(agent, mapa, destino)
            agent.persiguiendo = True
            agent.estado = "Persiguiendo (re-enfoque)"
        else:
            agent.persiguiendo = False
        return

    of, oc = agent.objetivo
    if not (0 <= of < FILAS and 0 <= oc < COLS) or mapa[of][oc] != CELDA_RATON:
        destino, _ = raton_visible_y_ruta(agent, mapa, VISION)
        if destino:
            _ruta_hacia(agent, mapa, destino)
            agent.persiguiendo = True
            agent.estado = "Persiguiendo (re-enfoque)"
        else:
            agent.persiguiendo = False
        return

    # Comparar por COSTO, no por longitud
    _, costo_restante = genetic_cost(mapa, (agent.fila, agent.col), [agent.objetivo])
    destino_cercano, ruta_cercana = raton_visible_y_ruta(agent, mapa, VISION)
    if not destino_cercano or not ruta_cercana:
        agent.persiguiendo = False
        return

    _, costo_cercano = genetic_cost(mapa, (agent.fila, agent.col), [destino_cercano])
    if costo_cercano + 1e-9 < costo_restante:
        _ruta_hacia(agent, mapa, destino_cercano)
        agent.persiguiendo = True
        agent.estado = "Re-enfocando al ratón visible más barato"
