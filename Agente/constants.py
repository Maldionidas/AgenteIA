# Agente/constants.py
VISION = 7                 # pasos máximos para "ver" (respeta muros)
COSTO_SPRINT = 1.5         # energía/step cuando persigue
COSTO_NORMAL = 1.0         # energía/step normal
JUEGO_MS = 2000            # 2s jugando con estambre
BEBER_MS = 7000            # 7s bebiendo leche
DRENA_JUEGO_POR_SEG = 0.4  # drenaje suave mientras juega
RECALC_COOLDOWN_MS = 300   # cooldown para re-enfoque de objetivo

# Lentitudes visuales (no cambian costos, solo pausan movimiento)
SLOW_MS_ALFOMBRA = 500     # 0.5s
SLOW_MS_AGUA = 1000        # 1.0s

# Visual de la ruta
PATH_RGBA = (0, 200, 255, 90)  # celeste translúcido

# Cooldown para NO encadenar pelotas (2s)
ESTAMBRE_COOLDOWN_MS = 2000
