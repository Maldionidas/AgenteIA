# Agente/interacciones.py
from .busquedaRuta import dijkstra, dijkstra_con_costo
from .percepcion import raton_mas_cercano, raton_visible_y_ruta, objetivo_visible_por_celda
from .constants import VISION, COSTO_SPRINT, COSTO_NORMAL
from config import FILAS, COLS, CELDA_RATON, CELDA_COMIDA, CELDA_ESTAMBRE
import pygame

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
        agent.yendo_por_leche = False  # ya llegó al plato
        mapa[agent.fila][agent.col] = 0  # consumir plato
        return True
    return False

def step_on_estambre(agent, mapa):
    # Condiciones para NO jugar:
    # - Cargando (rumbo a depósito)
    # - Yendo por leche
    # - En ruta/objetivo a BASE (cansancio al límite, ahorro energía)
    # - Flag explícito de ignorar estambre hasta llegar a base
    if agent.cargando or getattr(agent, "yendo_por_leche", False) \
       or agent.objetivo == agent.base or getattr(agent, "ignorar_estambre_hasta_base", False):
        return False

    # Cooldown global de 3s post-juego para no encadenar bolas
    ahora = pygame.time.get_ticks()
    if ahora < getattr(agent, "cooldown_estambre_hasta", 0):
        return False

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
        _, cp = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
        _, cd = dijkstra_con_costo(mapa, destino, [agent.deposito])
        _, cb = dijkstra_con_costo(mapa, agent.deposito, [agent.base])
        costo_total = cp + cd + cb

        if agent.energia.valor >= int(costo_total * 1.1):
            agent.estado = "Buscando ratón"
            agent.fue_deposito = False
            ruta, _ = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
            agent.ruta = ruta or []
            agent.ignorar_estambre_hasta_base = False
        else:
            agent.estado = "Cansancio al límite"
            agent.fue_deposito = True
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True  # *** NO jugar con estambre en ruta a base ***
    else:
        agent.estado = "Cansancio al límite"
        agent.fue_deposito = True
        agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
        agent.objetivo = agent.base
        agent.ignorar_estambre_hasta_base = True
    return True

# -------- PLATO con prioridad ABSOLUTA global (ignora todo menos depositar) --------
def _plato_mas_cercano(agent, mapa):
    platos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_COMIDA]
    if not platos:
        return None, None
    mejor = None
    mejor_ruta = None
    mejor_cost = None
    for p in platos:
        ruta, cost = dijkstra_con_costo(mapa, (agent.fila, agent.col), [p])
        if ruta:
            if mejor_cost is None or cost < mejor_cost:
                mejor, mejor_ruta, mejor_cost = p, ruta, cost
    return mejor, mejor_ruta

def prioridad_plato_fuerte(agent, mapa):
    # EXCEPCIÓN: si va a depositar (cargando) o ya bebiendo, NO interrumpir
    if agent.cargando or agent.bebiendo:
        return False
    obj, ruta = _plato_mas_cercano(agent, mapa)
    if obj and ruta:
        agent.jugando = False
        agent.recargando = False
        agent.persiguiendo = False
        agent.estado = "A por leche"
        agent.objetivo = obj
        agent.ruta = ruta
        agent.yendo_por_leche = True
        return True
    return False

# (Se conserva por compatibilidad; ya no se usa en el flujo principal)
def prioridad_plato(agent, mapa):
    obj, ruta = objetivo_visible_por_celda(agent, mapa, CELDA_COMIDA, VISION)
    if obj and ruta and obj != (agent.fila, agent.col) and not agent.bebiendo:
        agent.estado = "A por leche"
        agent.persiguiendo = False
        agent.ruta = ruta
        agent.objetivo = obj
        agent.yendo_por_leche = True
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
        agent.objetivo = agent.base
        agent.ignorar_estambre_hasta_base = True
        return True

    # 1) Estambre visible -> ir a jugar (salvo leche o ir a base)
    if not getattr(agent, "yendo_por_leche", False) and not getattr(agent, "ignorar_estambre_hasta_base", False):
        est_obj, est_ruta = objetivo_visible_por_celda(agent, mapa, CELDA_ESTAMBRE, VISION)
        if est_obj and est_ruta and est_obj != (agent.fila, agent.col):
            agent.estado = "Yendo a jugar"
            agent.persiguiendo = False
            agent.ruta = est_ruta
            agent.objetivo = est_obj
            return True

    # 2) Ratón visible -> perseguir (por costo)
    vis_obj, vis_ruta = raton_visible_y_ruta(agent, mapa, VISION)
    if vis_obj and vis_ruta and not getattr(agent, "yendo_por_leche", False):
        agent.estado = "Persiguiendo"
        agent.persiguiendo = True
        agent.energia.costo_paso = COSTO_SPRINT
        agent.ruta = vis_ruta
        agent.objetivo = vis_obj
        agent.ignorar_estambre_hasta_base = False
        return True

    # 3) Ir al más cercano si alcanza energía (por costo)
    destino = raton_mas_cercano(agent, mapa)
    if destino:
        ruta_pelota, cp = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
        _, cd = dijkstra_con_costo(mapa, destino, [agent.deposito])
        costo_hasta_depo = cp + cd

        if agent.energia.valor >= int(costo_hasta_depo * 1.1):
            agent.estado = "Buscando ratón"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = ruta_pelota or []
            agent.objetivo = destino
            agent.ignorar_estambre_hasta_base = False
            return True
        else:
            agent.estado = "Cansancio al límite"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True  # *** NO jugar con estambre en ruta a base ***
            return True

    agent.objetivo = None
    agent.persiguiendo = False
    agent.energia.costo_paso = COSTO_NORMAL
    return False

def salvaguarda_energia(agent, mapa):
    # Si vamos por leche, ignorar la salvaguarda
    if getattr(agent, "yendo_por_leche", False):
        return False
    if agent.cargando or (agent.fila, agent.col) == agent.base or agent.bebiendo or agent.jugando:
        return False
    ruta_base, _ = dijkstra_con_costo(mapa, (agent.fila, agent.col), [agent.base])
    costo_base = len(ruta_base) if ruta_base else 10 ** 9
    if agent.energia.valor <= (int(costo_base * 1.05) + 1):
        if agent.objetivo != agent.base:
            agent.estado = "Regresando a base (ahorro energía)"
            agent.persiguiendo = False
            agent.energia.costo_paso = COSTO_NORMAL
            agent.ruta = ruta_base or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True  # *** NO jugar con estambre en ruta a base ***
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
            ruta, _ = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
            agent.ruta = ruta or []
        return

    from config import CELDA_RATON
    if mapa[of][oc] != CELDA_RATON:
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
                ruta, _ = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
                agent.ruta = ruta or []
