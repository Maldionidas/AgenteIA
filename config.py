import pygame
#Configuración inicial
TAM = 40 #tamaño de las celdas en px
FILAS, COLS = 18, 28 #filas y columnas
ANCHO, ALTO = COLS * TAM, FILAS * TAM #dimension del mapa

# --- Tipos de celdas (IDs) ---
CELDA_VACIA = 0
CELDA_MURO = 1
CELDA_RATON = 2
CELDA_AGUA = 3
CELDA_ALFOMBRA = 4
CELDA_ESTAMBRE = 5    # NUEVO
CELDA_COMIDA = 6      # NUEVO

# Costos por celda
COSTOS = {
    CELDA_VACIA: 1,
    CELDA_RATON: 1,
    CELDA_AGUA: 2,
    CELDA_ALFOMBRA: 1.5,
    CELDA_COMIDA: 1,     # plato
    CELDA_ESTAMBRE: 1,   # bola
    CELDA_MURO: float("inf"),
}


# Colores de los objetos (solo fallback si faltan imágenes)
VACIO = (90, 90, 90)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)
JUGADOR = (50, 100, 255)
RATON_COLOR = (100, 100, 100)  # OJO: color, no ID

# Fuente para HUD
pygame.font.init()
FUENTE = pygame.font.SysFont("Arial", 24)

#casilla para recargar bombas
BASE = (1, 1)
DEPOSITO = (1, COLS-2)
VELOCIDAD = 9

# --- ENERGÍA Y PERSECUCIÓN DEL GATO ---
ENERGIA_MAX = 100.0          # tope de energía
ENERGIA_SPRINT_POR_PASO = 1.5 # costo por celda solo cuando persigue
ENERGIA_REGEN_POR_TICK = 4.0  # cuánto regenera por tick estando en la cama (BASE)

# Cada cuánto se mueve el gato (ms) — similar a los ratones para que se vea fluido
AGENTE_TICK_MS = 140

# --- Percepción y sprint del gato ---
VISION_CELDAS = 7            # alcance real en pasos (por ruta, respetando muros)
COSTO_PASO_NORMAL = 1.0
COSTO_PASO_CHASE  = 1.5      # costo por paso cuando está persiguiendo

# --- GA (planificación de ruta) ---
GA_HUNT_ENABLED = True   # activa GA para perseguir ratones (estado HUNT)

GA_PARAMS = dict(
    max_steps=120, pop_size=80, generations=80,
    p_crossover=0.90, p_mutation=0.08, tourn_k=3,
    wall_penalty=1000.0, step_cost=1.0, turn_cost=0.2,
    catch_bonus=1_000_000.0, deliver_bonus=1_000_000.0,
    terrain_cost_w=1.0,   # ← NUEVO: peso del costo de celda (COSTOS)
)


# consumo de energía por paso (ejemplo)
ENERGY_PER_STEP_EMPTY = 1.0      # sin ratón
ENERGY_PER_STEP_CARRY = 1.4      # cargando ratón

