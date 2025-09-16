import pygame
import random

#Configuración inicial
pygame.init()
TAM = 50 #tamaño de las celdas en px
FILAS, COLS = 11, 13 #filas y columnas
ANCHO, ALTO = COLS * TAM, FILAS * TAM #dimension del mapa
pantalla = pygame.display.set_mode((ANCHO, ALTO))# ventana
pygame.display.set_caption("Bomberman Grid Movement")#titulo

# Constantes de celdas
CELDA_VACIA = 0
CELDA_MURO = 1
CELDA_DESTRUIBLE = 2

# Colores de los objetos
VACIO = (200, 200, 200)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)
JUGADOR = (50, 100, 255)
BOMBA_COLOR = (0, 0, 0)   # negro para la bomba
LLAMA_COLOR = (255, 180, 0)  # naranja para la explosión
BASE_COLOR = (0, 0, 255)   # Azul para la base

# Bombas
FUSIBLE_MS = 1800
DURACION_LLAMA_MS = 350
ALCANCE_LLAMA = 1
MAX_BOMBAS = 3

# Fuente para HUD
pygame.font.init()
fuente = pygame.font.SysFont("Arial", 24)


def generar_mapa():
    mapa = []
    for fila in range(FILAS):
        fila_data = []
        for col in range(COLS):
            if fila == 0 or fila == FILAS-1 or col == 0 or col == COLS-1:
                fila_data.append(CELDA_MURO)
            elif fila % 2 == 0 and col % 2 == 0:
                fila_data.append(CELDA_MURO)
            else:
                fila_data.append(CELDA_DESTRUIBLE if random.random() < 0.3 else CELDA_VACIA)
        mapa.append(fila_data)

    # Zona inicial limpia
    mapa[1][1] = CELDA_VACIA
    mapa[1][2] = CELDA_VACIA
    mapa[2][1] = CELDA_VACIA
    return mapa

mapa = generar_mapa()

# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa):
        self.mapa = mapa
        self.base = base

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                if (fila, col) == self.base:
                    color = BASE_COLOR
                else:
                    color = VACIO if valor == CELDA_VACIA else MURO if valor == CELDA_MURO else DESTRUIBLE
                pygame.draw.rect(pantalla, color, (col*TAM, fila*TAM, TAM, TAM))
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

# --- Clase Jugador ---
class Jugador:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.x = col * TAM + TAM // 2
        self.y = fila * TAM + TAM // 2
        self.max_bombas = 3
        self.bombas_restantes = self.max_bombas
        #self.base = base

    def mover(self, teclas, mapa):
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            if mapa[self.fila - 1][self.col] == CELDA_VACIA:
                self.fila -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            if mapa[self.fila + 1][self.col] == CELDA_VACIA:
                self.fila += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            if mapa[self.fila][self.col - 1] == CELDA_VACIA:
                self.col -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            if mapa[self.fila][self.col + 1] == CELDA_VACIA:
                self.col += 1

        # Actualizar posición
        self.x = self.col * TAM + TAM // 2
        self.y = self.fila * TAM + TAM // 2
        
        
        #funcion para colocar las bombas
        def colocar_bomba(self, bombas, ahora):
            if self.bombas_restantes > 0:
                celda = (self.fila, self.col)
                if not any(b.celda == celda and not b.exploto for b in bombas):
                    bombas.append(Bomba(celda, ahora))
                    self.bombas_restantes -= 1

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, JUGADOR, (self.x, self.y), TAM//2 - 6)

# --- Clase Bomba ---
class Bomba:
    def __init__(self, celda, t_colocada):
        self.celda = celda
        self.t_colocada = t_colocada
        self.exploto = False
        self.t_explosion = None
        self.llamas = []

    def deberia_explotar(self, ahora):
        return (not self.exploto) and (ahora - self.t_colocada >= FUSIBLE_MS)

    def explotar(self, mapa):
        self.exploto = True
        self.t_explosion = pygame.time.get_ticks()
        f0, c0 = self.celda
        self.llamas = [(f0, c0)]
        for df, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            for paso in range(1, ALCANCE_LLAMA+1):
                f = f0 + df*paso
                c = c0 + dc*paso
                if not (0 <= f < FILAS and 0 <= c < COLS):
                    break
                if mapa[f][c] == CELDA_MURO:
                    break
                self.llamas.append((f, c))
                if mapa[f][c] == CELDA_DESTRUIBLE:
                    mapa[f][c] = CELDA_VACIA
                    break

    def llamas_activas(self, ahora):
        return self.exploto and (ahora - self.t_explosion <= DURACION_LLAMA_MS)

    def dibujar(self, pantalla, ahora):
        f, c = self.celda
        if not self.exploto:
            pygame.draw.circle(pantalla, BOMBA_COLOR,
                               (c*TAM + TAM//2, f*TAM + TAM//2), TAM//3)
        elif self.llamas_activas(ahora):
            for f, c in self.llamas:
                pygame.draw.rect(pantalla, LLAMA_COLOR,
                                 (c*TAM, f*TAM, TAM, TAM))

# --- Instancias ---
base = (1, 1)
escenario = Escenario(mapa)
jugador = Jugador(1, 1)
bombas = []

#contador de bombas
pygame.font.init()
fuente = pygame.font.SysFont("Arial", 24)  # fuente para el contador


# --- Bucle principal ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    ahora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:  # colocar bomba
                if jugador.bombas_restantes > 0:
                    celda = (jugador.fila, jugador.col)
                    if not any(b.celda == celda and not b.exploto for b in bombas):
                        bombas.append(Bomba(celda, ahora))
                        jugador.bombas_restantes -= 1
                else:
                    print("¡No puedes poner más bombas! Recarga en la base.")


    teclas = pygame.key.get_pressed()
    jugador.mover(teclas, mapa)
     # Recargar bombas si está en la base
    if jugador.fila == 1 and jugador.col == 1:
        jugador.bombas_restantes = jugador.max_bombas


    # Explosiones
    for b in bombas:
        if b.deberia_explotar(ahora):
            b.explotar(mapa)

    # --- Dibujo ---
    pantalla.fill((0, 0, 0))
    escenario.dibujar(pantalla)
    jugador.dibujar(pantalla)

    for b in bombas:
        b.dibujar(pantalla, ahora)
    # Dibujar contador de bombas
    texto = fuente.render(f"Bombas: {jugador.bombas_restantes}", True, (255,255,255))
    pantalla.blit(texto, (10, 10))  # posición arriba a la izquierda


    pygame.display.flip()
    clock.tick(10)

pygame.quit()
