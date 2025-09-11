import pygame
import random

# --- Configuración inicial ---
pygame.init()
TAM = 50
FILAS, COLS = 11, 13
ANCHO, ALTO = COLS * TAM, FILAS * TAM
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Bomberman Grid Movement")

# Colores
VACIO = (200, 200, 200)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)
JUGADOR = (50, 100, 255)

# --- Generar mapa ---
def generar_mapa():
    mapa = []
    for fila in range(FILAS):
        fila_data = []
        for col in range(COLS):
            if fila == 0 or fila == FILAS-1 or col == 0 or col == COLS-1:
                fila_data.append(1)
            elif fila % 2 == 0 and col % 2 == 0:
                fila_data.append(1)
            else:
                fila_data.append(2 if random.random() < 0.3 else 0)
        mapa.append(fila_data)
    # Limpiar zona inicial
    mapa[1][1] = 0
    mapa[1][2] = 0
    mapa[2][1] = 0
    return mapa

mapa = generar_mapa()

# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa):
        self.mapa = mapa

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                color = VACIO if valor == 0 else MURO if valor == 1 else DESTRUIBLE
                pygame.draw.rect(pantalla, color, (col*TAM, fila*TAM, TAM, TAM))
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

# --- Clase Jugador Grid ---
class Jugador:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.x = col * TAM + TAM // 2
        self.y = fila * TAM + TAM // 2

    def mover(self, teclas, mapa):
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            if mapa[self.fila - 1][self.col] == 0:
                self.fila -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            if mapa[self.fila + 1][self.col] == 0:
                self.fila += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            if mapa[self.fila][self.col - 1] == 0:
                self.col -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            if mapa[self.fila][self.col + 1] == 0:
                self.col += 1

        # Actualizar posición visual
        self.x = self.col * TAM + TAM // 2
        self.y = self.fila * TAM + TAM // 2

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, JUGADOR, (self.x, self.y), TAM//2 - 6)

# --- Instancias ---
escenario = Escenario(mapa)
jugador = Jugador(1, 1)  # empieza en la esquina superior izquierda

# --- Bucle principal ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    teclas = pygame.key.get_pressed()
    jugador.mover(teclas, mapa)

    pantalla.fill((0, 0, 0))
    escenario.dibujar(pantalla)
    jugador.dibujar(pantalla)
    pygame.display.flip()
    clock.tick(10)  # 10 FPS para ver claramente el movimiento por casilla

pygame.quit()
