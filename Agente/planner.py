# Agente/planner.py
from config import FILAS, COLS, CELDA_RATON
from .busquedaRuta import dijkstra
from .percepcion import raton_visible_y_ruta

def _ruta_hacia(agent, mapa, destino):
    agent.objetivo = destino
    agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []

def recalcular_si_conviene(agent, mapa, VISION, cooldown_ms):
    if agent.cargando or agent.animando or agent.fue_deposito:
        return
    if not agent.ruta:
        return

    ahora = agent._ticks()
    if ahora - agent._ultimo_recalculo < cooldown_ms:
        return
    agent._ultimo_recalculo = ahora

    # Si el objetivo dejó de ser un ratón válido, buscar otro SOLO si está en visión
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
        destino, ruta_vis = raton_visible_y_ruta(agent, mapa, VISION)
        if destino:
            _ruta_hacia(agent, mapa, destino)
            agent.persiguiendo = True
            agent.estado = "Persiguiendo (re-enfoque)"
        else:
            agent.persiguiendo = False
        return

    # Comparar longitudes de ruta pero solo con un ratón VISIBLE
    ruta_restante_len = len(agent.ruta)
    destino_cercano, ruta_cercana = raton_visible_y_ruta(agent, mapa, VISION)
    if not destino_cercano or not ruta_cercana:
        agent.persiguiendo = False
        return

    if destino_cercano == agent.objetivo:
        return

    if len(ruta_cercana) < ruta_restante_len:
        _ruta_hacia(agent, mapa, destino_cercano)
        agent.persiguiendo = True
        agent.estado = "Re-enfocando al ratón visible más cercano"
