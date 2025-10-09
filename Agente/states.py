# Agente/states.py
import pygame
from .busquedaRuta import dijkstra
from .percepcion import raton_mas_cercano, raton_visible_y_ruta, objetivo_visible_por_celda
from .constants import (VISION, COSTO_SPRINT, COSTO_NORMAL, JUEGO_MS, BEBER_MS,
                        DRENA_JUEGO_POR_SEG)
from config import FILAS, COLS, CELDA_RATON, CELDA_COMIDA, CELDA_ESTAMBRE

def ensure_runtime_flags(agent):
    if not hasattr(agent, "persiguiendo"):
        agent.persiguiendo = False
    if not hasattr(agent, "jugando"):
        agent.jugando = False
        agent.inicio_juego = 0
        agent.tiempo_juego_ms = JUEGO_MS
        agent._ultimo_tick_juego = pygame.time.get_ticks()
    if not hasattr(agent, "bebiendo"):
        agent.bebiendo = False
        agent.inicio_bebida = 0
        agent.tiempo_bebida_ms = BEBER_MS
    if not hasattr(agent, "_evitar_retrigger_estambre"):
        agent._evitar_retrigger_estambre = False
    if not hasattr(agent, "_evitar_retrigger_leche"):
        agent._evitar_retrigger_leche = False

def handle_bebiendo(agent, mapa):
    if not agent.bebiendo:
        return False
    agent.estado = "Bebiendo leche"
    if pygame.time.get_ticks() - agent.inicio_bebida >= agent.tiempo_bebida_ms:
        agent.bebiendo = False
        agent.energia.valor = agent.energia.energia_max
        agent.estado = "Energía recuperada"
    return True  # se queda quieto durante la bebida

def handle_jugando(agent, mapa):
    if not agent.jugando:
        return False
    ahora = pygame.time.get_ticks()
    delta = (ahora - getattr(agent, "_ultimo_tick_juego", ahora)) / 1000.0
    agent._ultimo_tick_juego = ahora
    if agent.energia.valor > 0:
        agent.energia.valor = max(0, agent.energia.valor - DRENA_JUEGO_POR_SEG * delta)

    agent.estado = "Jugando con estambre"
    if ahora - agent.inicio_juego >= agent.tiempo_juego_ms:
        agent.jugando = False
        agent.estado = "Listo"
    elif agent.energia.valor <= 0 and (agent.fila, agent.col) != agent.base:
        agent.jugando = False
        agent.persiguiendo = False
        agent.estado = "Sin energía, regresando a base"
        agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
    return True

def handle_sin_energia(agent, mapa):
    if agent.energia.valor > 0 or (agent.fila, agent.col) == agent.base:
        return False
    agent.persiguiendo = False
    agent.estado = "Sin energía, regresando a base"
    if agent.objetivo != agent.base or not agent.ruta:
        agent.ruta = dijkstra(mapa, (agent.fila, agent.col), [agent.base]) or []
    if agent.ruta:
        accion = agent.ruta.pop(0)
        agent.mover(accion, mapa)
    return True

def handle_en_base_y_recarga(agent, mapa):
    if (agent.fila, agent.col) != agent.base:
        return False

    agent.persiguiendo = False
    ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
    n_restantes = len(ratones)

    if n_restantes > 0:
        if n_restantes >= 4:
            objetivo_carga = agent.energia.energia_max
        else:
            destino = raton_mas_cercano(agent, mapa)
            if destino:
                ruta_pelota = dijkstra(mapa, (agent.fila, agent.col), [destino]) or []
                ruta_depo = dijkstra(mapa, destino, [agent.deposito]) or []
                ruta_base = dijkstra(mapa, agent.deposito, [agent.base]) or []
                costo_ciclo = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)
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
