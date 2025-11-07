# Agente/states.py
import pygame
from .geneticAlg import genetic_shortest, genetic_cost, genetic_route
from .percepcion import raton_mas_cercano
from .constants import (VISION, COSTO_SPRINT, COSTO_NORMAL, JUEGO_MS, BEBER_MS,
                        DRENA_JUEGO_POR_SEG, ESTAMBRE_COOLDOWN_MS)
from config import FILAS, COLS, CELDA_RATON, CELDA_COMIDA, CELDA_ESTAMBRE

def ensure_runtime_flags(agent):
    # Flags base
    if not hasattr(agent, "persiguiendo"): agent.persiguiendo = False
    if not hasattr(agent, "jugando"): agent.jugando = False
    if not hasattr(agent, "bebiendo"): agent.bebiendo = False
    if not hasattr(agent, "yendo_por_leche"): agent.yendo_por_leche = False

    # Jugando (timers)
    if not hasattr(agent, "inicio_juego"): agent.inicio_juego = 0
    if not hasattr(agent, "tiempo_juego_ms"): agent.tiempo_juego_ms = JUEGO_MS
    if not hasattr(agent, "_ultimo_tick_juego"): agent._ultimo_tick_juego = pygame.time.get_ticks()

    # Bebiendo (timers)
    if not hasattr(agent, "inicio_bebida"): agent.inicio_bebida = 0
    if not hasattr(agent, "tiempo_bebida_ms"): agent.tiempo_bebida_ms = BEBER_MS

    # Anti-retrigger / cooldowns
    if not hasattr(agent, "_evitar_retrigger_estambre"): agent._evitar_retrigger_estambre = False
    if not hasattr(agent, "_evitar_retrigger_leche"): agent._evitar_retrigger_leche = False
    if not hasattr(agent, "cooldown_estambre_hasta"): agent.cooldown_estambre_hasta = 0
    if not hasattr(agent, "ignorar_estambre_hasta_base"): agent.ignorar_estambre_hasta_base = False
    if not hasattr(agent, "_evitar_descanso_hasta"): agent._evitar_descanso_hasta = 0


def handle_bebiendo(agent, mapa):
    if not agent.bebiendo:
        return False
    agent.estado = "Bebiendo leche"
    ahora = pygame.time.get_ticks()
    if ahora - agent.inicio_bebida >= agent.tiempo_bebida_ms:
        # Termina de beber: energía al máximo e ir a perseguir ratón (no descansar)
        agent.bebiendo = False
        agent.energia.valor = agent.energia.energia_max
        agent.yendo_por_leche = False
        agent.recargando = False
        agent._evitar_descanso_hasta = ahora + 1500  # antirebote de descanso
        destino = raton_mas_cercano(agent, mapa)
        if destino:
            #ruta, _ = dijkstra_con_costo(mapa, (agent.fila, agent.col), [destino])
            #agent.ruta = ruta or []
            # Inicia con GA (acciones); si nada, fallback a Dijkstra:
            agent.ruta = genetic_route(mapa, (agent.fila, agent.col), destino,
                                       mode="HUNT",
                                       energia_restante=agent.energia.valor,
                                       cargando=False) or (genetic_shortest(mapa, (agent.fila, agent.col), [destino]) or [])
            agent.objetivo = destino
            agent.persiguiendo = True
            agent.estado = "Persiguiendo"
        else:
            agent.estado = "Listo"
    return True

def handle_jugando(agent, mapa):
    if not agent.jugando:
        return False
   # Guardar de seguridad: si por alguna razón faltan timers, créalos aquí.
    if not hasattr(agent, "tiempo_juego_ms"):
        agent.tiempo_juego_ms = JUEGO_MS
    if not hasattr(agent, "inicio_juego"):
        agent.inicio_juego = agent._ticks()
    if not hasattr(agent, "_ultimo_tick_juego"):
        agent._ultimo_tick_juego = agent._ticks()
    ahora = pygame.time.get_ticks()
    delta = (ahora - getattr(agent, "_ultimo_tick_juego", ahora)) / 1000.0
    agent._ultimo_tick_juego = ahora
    if agent.energia.valor > 0:
        agent.energia.valor = max(0, agent.energia.valor - DRENA_JUEGO_POR_SEG * delta)

    agent.estado = "Jugando con estambre"
    if ahora - agent.inicio_juego >= agent.tiempo_juego_ms:
        agent.jugando = False
        agent.estado = "Listo"
        agent.cooldown_estambre_hasta = ahora + ESTAMBRE_COOLDOWN_MS  # *** 2s ***
    elif agent.energia.valor <= 0 and (agent.fila, agent.col) != agent.base:
        agent.jugando = False
        agent.persiguiendo = False
        agent.estado = "Sin energía, regresando a base"
        agent.cooldown_estambre_hasta = ahora + ESTAMBRE_COOLDOWN_MS
        agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
    return True

def handle_sin_energia(agent, mapa):
    if agent.energia.valor > 0 or (agent.fila, agent.col) == agent.base:
        return False
    agent.persiguiendo = False
    agent.estado = "Sin energía, regresando a base"
    if agent.objetivo != agent.base or not agent.ruta:
        agent.ruta = genetic_shortest(mapa, (agent.fila, agent.col), [agent.base]) or []
    if agent.ruta:
        accion = agent.ruta.pop(0)
        agent.mover(accion, mapa)
    return True

def handle_en_base_y_recarga(agent, mapa):
    if (agent.fila, agent.col) == agent.base:
        if pygame.time.get_ticks() < getattr(agent, "_evitar_descanso_hasta", 0):
            agent.recargando = False
            return False
    if (agent.fila, agent.col) != agent.base:
        return False

    agent.persiguiendo = False
    agent.ignorar_estambre_hasta_base = False

    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    n_restantes = len(ratones)

    if n_restantes > 0:
        if n_restantes >= 4:
            objetivo_carga = agent.energia.energia_max
        else:
            destino = raton_mas_cercano(agent, mapa)
            if destino:
                _, cp = genetic_cost(mapa, (agent.fila, agent.col), [destino])
                _, cd = genetic_cost(mapa, destino, [agent.deposito])
                _, cb = genetic_cost(mapa, agent.deposito, [agent.base])
                costo_ciclo = cp + cd + cb
                objetivo_carga = min(agent.energia.energia_max, int(costo_ciclo * n_restantes * 1.2))
            else:
                objetivo_carga = agent.energia.energia_max
    else:
        objetivo_carga = agent.energia.energia_max

    if agent.energia.valor < objetivo_carga:
        agent.estado = "Descansando"
        agent.recargando = True
        ahora = agent._ticks()
        delta_ms = ahora - agent.ultimo_tick
        recarga = (delta_ms / 1000) * agent.energia.recarga_por_segundo
        agent.energia.valor = min(objetivo_carga, agent.energia.valor + recarga)
        agent.ultimo_tick = ahora
        return True
    else:
        agent.recargando = False
        agent.ultimo_tick = agent._ticks()
        return False
