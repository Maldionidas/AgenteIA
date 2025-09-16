import pygame
import random

# =========================
# Config base del escenario
# =========================
pygame.init()
TAM = 50                        # tamaño de cada casilla
FILAS, COLS = 11, 13            # tamaño del mapa
ANCHO, ALTO = COLS*TAM, FILAS*TAM
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Bomberman con Gatito")

# Colores de celdas
VACIO = (200, 200, 200)
MURO = (60, 60, 60)
DESTRUIBLE = (160, 100, 40)

DEBUG_CROSSHAIR = False  # pon True para ver cruz roja en el centro del jugador

# =========================
# Generación del mapa
# =========================
def generar_mapa():
    mapa = []
    for fila in range(FILAS):
        fila_data = []
        for col in range(COLS):
            if fila == 0 or fila == FILAS-1 or col == 0 or col == COLS-1:
                fila_data.append(1)  # borde
            elif fila % 2 == 0 and col % 2 == 0:
                fila_data.append(1)  # muros sólidos en patrón
            else:
                fila_data.append(2 if random.random() < 0.3 else 0)
        mapa.append(fila_data)

    # Limpiar zona inicial del jugador (esquina superior izquierda)
    mapa[1][1] = 0
    mapa[1][2] = 0
    mapa[2][1] = 0

    return mapa

mapa = generar_mapa()

# =========================
# Clases
# =========================
class Escenario:
    def __init__(self, mapa):
        self.mapa = mapa

    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                if valor == 0:
                    color = VACIO
                elif valor == 1:
                    color = MURO
                else:  # 2
                    color = DESTRUIBLE

                pygame.draw.rect(pantalla, color, (col*TAM, fila*TAM, TAM, TAM))
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = TAM - 5      # hitbox
        self.alto = TAM - 5
        self.vel = 3

        # ==== Cargar sprites del gatito ====
        self.sprites = {
            "front": pygame.transform.scale(pygame.image.load("cat_front.png").convert_alpha(), (TAM - 6, TAM - 6)),
            "back": pygame.transform.scale(pygame.image.load("cat_back.png").convert_alpha(), (TAM - 6, TAM - 6)),
            "left": pygame.transform.scale(pygame.image.load("cat_left.png").convert_alpha(), (TAM - 6, TAM - 6)),
            "right": pygame.transform.scale(pygame.image.load("cat_right.png").convert_alpha(), (TAM - 6, TAM - 6)),
        }

        self.direction = "front"  # vista inicial
        self.sprite = self.sprites[self.direction]

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.ancho//2,
            self.y - self.alto//2,
            self.ancho,
            self.alto
        )

    def mover(self, teclas, mapa):
        dx, dy = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy = -self.vel
            self.direction = "back"
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy = self.vel
            self.direction = "front"
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx = -self.vel
            self.direction = "left"
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx = self.vel
            self.direction = "right"

        nuevo_rect = self.rect.move(dx, dy)
        if not self.colisiona(nuevo_rect, mapa):
            self.x += dx
            self.y += dy

        # actualizar sprite según dirección
        self.sprite = self.sprites[self.direction]

    def colisiona(self, rect, mapa):
        esquinas = [
            (rect.left, rect.top),
            (rect.right-1, rect.top),
            (rect.left, rect.bottom-1),
            (rect.right-1, rect.bottom-1)
        ]
        for px, py in esquinas:
            fila = py // TAM
            col = px // TAM
            if mapa[fila][col] != 0:
                return True
        return False

    def dibujar(self, pantalla):
        r = self.sprite.get_rect(center=(self.x, self.y))
        pantalla.blit(self.sprite, r)

        if DEBUG_CROSSHAIR:
            cx, cy = self.x, self.y
            pygame.draw.line(pantalla, (255, 0, 0), (cx-5, cy), (cx+5, cy), 1)
            pygame.draw.line(pantalla, (255, 0, 0), (cx, cy-5), (cx, cy+5), 1)

# =========================
# Instancias y loop
# =========================
escenario = Escenario(mapa)
jugador = Jugador(TAM + TAM//2, TAM + TAM//2)  # empieza en [1][1]

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
    clock.tick(60)

pygame.quit()
