# Agente/interacciones.py
from .busquedaRuta import dijkstra
from .percepcion import raton_mas_cercano, raton_visible_y_ruta, objetivo_visible_por_celda
from .constants import VISION, COSTO_SPRINT, COSTO_NORMAL
from config import CELDA_RATON, CELDA_COMIDA, CELDA_ESTAMBRE

def step_on_raton(agent, mapa):
    if agent.cargando or agent.fue_deposito:
        return False
    if mapa[agent.fila][agent.col] == CELDA_RATON:
        agent.animando = True
        agent.inicio_animacion = agent._ticks()
        agent.estado = "Recogiendo ratón"
        agent.objetivo = None
        agent.ruta = []
        agent.persiguiendo = False
        mapa[agent.fila][agent.col] = 0  # CELDA_VACIA
        return True
    return False

def end_pick_animation_if_done(agent, mapa):
    if not agent.animando:
        return False
    agent.estado = "Recogiendo ratón"
    ahora = agent._ticks()
    if ahora - agent.inicio_animacion >= agent.tiempo_animacion:
        agent.animando = False
        agent.cargando = True
        mapa[agent.fila][agent.col] = 0  # CELDA_VACIA
        agent.estado = "Yendo a depositar ratón"
        agent.persiguiendo = False
        if agent.deposito:
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.deposito]) or []
    return True

def step_on_plato(agent, mapa):
    if mapa[agent.fila][agent.col] == CELDA_COMIDA and not agent._evitar_retrigger_leche:
        agent.estado = "Bebiendo leche"
        agent.bebiendo = True
        agent.inicio_bebida = agent._ticks()
        agent.objetivo = None
        agent.ruta = []
        agent.persiguiendo = False
        agent._evitar_retrigger_leche = True
        mapa[agent.fila][agent.col] = 0  # CELDA_VACIA
        return True
    return False

def step_on_estambre(agent, mapa):
    if mapa[agent.fila][agent.col] == CELDA_ESTAMBRE and not agent._evitar_retrigger_estambre:
        agent.estado = "Jugando con estambre"
        agent.jugando = True
        agent.inicio_juego = agent._ticks()
        agent._ultimo_tick_juego = agent.inicio_juego
        agent.objetivo = None
        agent.ruta = []
        agent.persiguiendo = False
        agent._evitar_retrigger_estambre = True
        return True
    return False

def handle_deposito(agent, mapa):
    if not (agent.cargando and (agent.fila, agent.col) == agent.deposito):
        return False
    agent.cargando = False
    agent.contador_deposito += 1
    agent.objetivo = None
    agent.ruta = []
    agent.persiguiendo = False

    destino = raton_mas_cercano(agent, mapa)
    if destino:
        ruta_pelota = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
        ruta_depo = dijkstra(mapa, destino, [agent.deposito]) or []
        ruta_base = dijkstra(mapa, agent.deposito, [agent.base]) or []
        costo_total = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)

        if agent.energia.valor >= int(costo_total * 1.1):
            agent.estado = "Buscando ratón"
            agent.fue_deposito = False
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
        else:
            agent.estado = "Cansancio al límite"
            agent.fue_deposito = True
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
    else:
        agent.estado = "Cansancio al límite"
        agent.fue_deposito = True
        agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
    return True

def prioridad_plato(agent, mapa):
    obj, ruta = objetivo_visible_por_celda(agent, mapa, CELDA_COMIDA, VISION)
    if obj and ruta and obj != (agent.fila, agent.col) and not agent.bebiendo:
        agent.estado = "A por leche"
        agent.persiguiendo = False
        agent.ruta = ruta
        agent.objetivo = obj
        return True
    return False

def planear_si_no_hay_ruta(agent, mapa):
    if agent.ruta:
        return False
    if agent.cargando:
        agent.estado = "Yendo a depositar ratón"
        if agent.deposito:
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.deposito]) or []
        return True

    if agent.fue_deposito:
        agent.estado = "Descansando"
        agent.persiguiendo = False
        agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
        return True

    # 1) Estambre visible -> ir a jugar
    est_obj, est_ruta = objetivo_visible_por_celda(agent, mapa, CELDA_ESTAMBRE, VISION)
    if est_obj and est_ruta and est_obj != (agent.fila, agent.col):
        agent.estado = "Yendo a jugar"
        agent.persiguiendo = False
        agent.ruta = est_ruta
        agent.objetivo = est_obj
        return True

    # 2) Raton visible -> perseguir (gasta 1.5/step)
    vis_obj, vis_ruta = raton_visible_y_ruta(agent, mapa, VISION)
    if vis_obj and vis_ruta:
        agent.estado = "Persiguiendo"
        agent.persiguiendo = True
        agent.energia.costo_paso = COSTO_SPRINT
        agent.ruta = vis_ruta
        agent.objetivo = vis_obj
        return True

    # 3) Ir al más cercano si alcanza energía
    destino = raton_mas_cercano(agent, mapa)
    if destino:
        ruta_pelota = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
        ruta_depo = dijkstra(mapa, destino, [agent.deposito]) or []
        costo_hasta_depo = len(ruta_pelota) + len(ruta_depo)

        if agent.energia.valor >= int(costo_hasta_depo * 1.1):
            agent.estado = "Buscando ratón"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = ruta_pelota
            agent.objetivo = destino
            return True
        else:
            agent.estado = "Cansancio al límite"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
            agent.objetivo = agent.base
            return True

    agent.objetivo = None
    agent.persiguiendo = False
    agent.energia.costo_paso = COSTO_NORMAL
    return False

def salvaguarda_energia(agent, mapa):
    if agent.cargando or (agent.fila, agent.col) == agent.base or agent.bebiendo or agent.jugando:
        return False
    ruta_base_tmp = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
    costo_base = len(ruta_base_tmp) if ruta_base_tmp else 10 ** 9
    if agent.energia.valor <= (int(costo_base * 1.05) + 1):
        if agent.objetivo != agent.base:
            agent.estado = "Regresando a base (ahorro energía)"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = ruta_base_tmp
            agent.objetivo = agent.base
            return True
    return False

def mantener_persecucion_o_volver_flujo(agent, mapa):
    if not agent.persiguiendo:
        return
    of, oc = agent.objetivo or (-1, -1)
    if agent.objetivo is None:
        agent.persiguiendo = False
        agent.energia.costo_paso = COSTO_NORMAL
        agent.estado = "Buscando ratón"
        destino = raton_mas_cercano(agent, mapa)
        if destino:
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
        return

    # si objetivo dejó de ser ratón, reintenta con visible, si no, caer a normal
    from config import FILAS, COLS, CELDA_RATON
    if not (0 <= of < FILAS and 0 <= oc < COLS) or mapa[of][oc] != CELDA_RATON:
        vis_obj, vis_ruta = raton_visible_y_ruta(agent, mapa, VISION)
        if vis_obj and vis_ruta:
            agent.ruta = vis_ruta
            agent.objetivo = vis_obj
            agent.estado = "Persiguiendo"
        else:
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.estado = "Buscando ratón"
            destino = raton_mas_cercano(agent, mapa)
            if destino:
                agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
