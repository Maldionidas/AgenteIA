# Agente/interacciones.py
import pygame
from .geneticAlg import genetic_shortest, genetic_cost, genetic_route
from .percepcion import raton_mas_cercano, raton_visible_y_ruta, objetivo_visible_por_celda
from .constants import VISION, COSTO_SPRINT, COSTO_NORMAL, ESTAMBRE_COOLDOWN_MS
from config import FILAS, COLS, CELDA_RATON, CELDA_COMIDA, CELDA_ESTAMBRE

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
        mapa[agent.fila][agent.col] = 0
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
        mapa[agent.fila][agent.col] = 0
        agent.estado = "Yendo a depositar ratón"
        agent.persiguiendo = False
        if agent.deposito:
            agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.deposito]) or []
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
        agent.yendo_por_leche = False
        mapa[agent.fila][agent.col] = 0
        return True
    return False

def step_on_estambre(agent, mapa):
    # NO jugar si: cargando, yendo a leche, rumbo/base, ignorar hasta base
    if agent.cargando or getattr(agent, "yendo_por_leche", False) \
       or agent.objetivo == agent.base or getattr(agent, "ignorar_estambre_hasta_base", False):
        return False
    # cooldown global de 2s para no encadenar bolas
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
        _, cp = genetic_cost(mapa, (agent.fila, agent.col), [destino])
        _, cd = genetic_cost(mapa, destino, [agent.deposito])
        _, cb = genetic_cost(mapa, agent.deposito, [agent.base])
        costo_total = cp + cd + cb

        if agent.energia.valor >= int(costo_total * 1.1):
            agent.estado = "Buscando ratón"
            agent.fue_deposito = False
            ruta, _ = genetic_cost(mapa, (agent.fila, agent.col), [destino])
            agent.ruta = ruta or []
            agent.ignorar_estambre_hasta_base = False
        else:
            agent.estado = "Cansancio al límite"
            agent.fue_deposito = True
            agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True
    else:
        agent.estado = "Cansancio al límite"
        agent.fue_deposito = True
        agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
        agent.objetivo = agent.base
        agent.ignorar_estambre_hasta_base = True
    return True

# ---- utilidades de objetivos globales ----
def _plato_mas_cercano(agent, mapa):
    platos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_COMIDA]
    if not platos:
        return None, None
    mejor = None; mejor_ruta = None; mejor_cost = None
    for p in platos:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and (mejor_cost is None or cost < mejor_cost):
            mejor, mejor_ruta, mejor_cost = p, ruta, cost
    return mejor, mejor_ruta

def _estambre_mas_cercano(agent, mapa):
    ests = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_ESTAMBRE]
    if not ests:
        return None, None
    mejor = None; mejor_ruta = None; mejor_cost = None
    for p in ests:
        ruta, cost = genetic_cost(mapa, (agent.fila, agent.col), [p])
        if ruta and (mejor_cost is None or cost < mejor_cost):
            mejor, mejor_ruta, mejor_cost = p, ruta, cost
    return mejor, mejor_ruta

# ---- prioridad plato absoluta ----
def prioridad_plato_fuerte(agent, mapa):
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

# ---- planeación principal (respeta cooldown de estambre) ----
def planear_si_no_hay_ruta(agent, mapa):
    if agent.ruta:
        return False
    if agent.cargando:
        agent.estado = "Yendo a depositar ratón"
        if agent.deposito:
            agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.deposito]) or []
        return True

    if agent.fue_deposito:
        agent.estado = "Descansando"
        agent.persiguiendo = False
        agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
        agent.objetivo = agent.base
        agent.ignorar_estambre_hasta_base = True
        return True

    ahora = pygame.time.get_ticks()
    en_cooldown_estambre = ahora < getattr(agent, "cooldown_estambre_hasta", 0)

    # --- MODO OCIO: sin ratones ---
    hay_ratones = any(mapa[f][c] == CELDA_RATON for f in range(FILAS) for c in range(COLS))
    if not hay_ratones:
        if not en_cooldown_estambre:
            est_obj, est_ruta = _estambre_mas_cercano(agent, mapa)
            if est_obj and est_ruta:
                agent.estado = "Yendo a jugar"
                agent.persiguiendo = False
                agent.ruta = est_ruta
                agent.objetivo = est_obj
                agent.ignorar_estambre_hasta_base = False
                return True
        # en cooldown: ir a base a esperar/plato
        agent.estado = "Descansando"
        agent.persiguiendo = False
        agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
        agent.objetivo = agent.base
        agent.ignorar_estambre_hasta_base = True
        return True

    # --- flujo normal con ratones ---
    # 1) Estambre visible -> ir a jugar (solo si NO cooldown, NO leche, NO rumbo a base)
    if (not getattr(agent, "yendo_por_leche", False)
        and not getattr(agent, "ignorar_estambre_hasta_base", False)
        and not en_cooldown_estambre):
        est_obj, est_ruta = objetivo_visible_por_celda(agent, mapa, CELDA_ESTAMBRE, VISION)
        if est_obj and est_ruta and est_obj != (agent.fila, agent.col):
            agent.estado = "Yendo a jugar"
            agent.persiguiendo = False
            agent.ruta = est_ruta
            agent.objetivo = est_obj
            return True

    # 2) Ratón visible -> perseguir
    vis_obj, vis_ruta = raton_visible_y_ruta(agent, mapa, VISION)
    if vis_obj and not getattr(agent, "yendo_por_leche", False):
        agent.estado = "Persiguiendo"
        agent.persiguiendo = True
        # GA para HUNT (acciones):
        agent.ruta = genetic_route(mapa, (agent.fila, agent.col), vis_obj,
                                   mode="HUNT",
                                   energia_restante=agent.energia.valor,
                                   cargando=False) or []
        agent.objetivo = vis_obj
        agent.ignorar_estambre_hasta_base = False
        return True

    # 3) Ratón más cercano por costo
    destino = raton_mas_cercano(agent, mapa)
    if destino:
        ruta_pelota, cp = genetic_cost(mapa, (agent.fila, agent.col), [destino])
        _, cd = genetic_cost(mapa, destino, [agent.deposito])
        costo_hasta_depo = cp + cd
        if agent.energia.valor >= int(costo_hasta_depo * 1.1):
            agent.estado = "Buscando ratón"
            agent.persiguiendo = False
            #agent.ruta = ruta_pelota or []
            agent.ruta = genetic_route(mapa, (agent.fila, agent.col), destino,
                                       mode="HUNT",
                                       energia_restante=agent.energia.valor,
                                       cargando=False) or (ruta_pelota or [])
            agent.objetivo = destino
            agent.ignorar_estambre_hasta_base = False
            return True
        else:
            agent.estado = "Cansancio al límite"
            agent.persiguiendo = False
            agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True
            return True

    agent.objetivo = None
    agent.persiguiendo = False
    return False

def salvaguarda_energia(agent, mapa):
    if getattr(agent, "yendo_por_leche", False):
        return False
    if agent.cargando or (agent.fila, agent.col) == agent.base or agent.bebiendo or agent.jugando:
        return False
    ruta_base, _ = genetic_cost(mapa, (agent.fila, agent.col), [agent.base])
    costo_base = len(ruta_base) if ruta_base else 10 ** 9
    if agent.energia.valor <= (int(costo_base * 1.05) + 1):
        if agent.objetivo != agent.base:
            agent.estado = "Regresando a base (ahorro energía)"
            agent.persiguiendo = False
            agent.ruta = ruta_base or []
            agent.objetivo = agent.base
            agent.ignorar_estambre_hasta_base = True
            return True
    return False

def mantener_persecucion_o_volver_flujo(agent, mapa):
    if not agent.persiguiendo:
        return
    of, oc = agent.objetivo or (-1, -1)
    if agent.objetivo is None:
        agent.persiguiendo = False
        agent.estado = "Buscando ratón"
        destino = raton_mas_cercano(agent, mapa)
        if destino:
            ruta, _ = genetic_cost(mapa, (agent.fila, agent.col), [destino])
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
            agent.estado = "Buscando ratón"
            destino = raton_mas_cercano(agent, mapa)
            if destino:
                ruta, _ = genetic_cost(mapa, (agent.fila, agent.col), [destino])
                agent.ruta = ruta or []
