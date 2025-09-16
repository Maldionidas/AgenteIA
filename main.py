import pygame
import random
from config import ANCHO, ALTO, FUENTE, BASE
from mapa import generar_mapa
from escenario import Escenario
from jugador import Jugador
from bomba import Bomba

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))# ventana
pygame.display.set_caption("Bomberman Grid Movement")#titulo

# --- Instancias ---
mapa = generar_mapa()
escenario = Escenario(mapa, BASE)
jugador = Jugador(1, 1)  # posición inicial del jugador
bombas = []  # lista de bombas


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
                    #celda = (jugador.fila, jugador.col)
                    if not any(not b.exploto for b in bombas):
                        celda = (jugador.fila, jugador.col)
                        bombas.append(Bomba(celda, ahora))
                        jugador.bombas_restantes -= 1
                


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
    texto = FUENTE.render(f"Bombas: {jugador.bombas_restantes}", True, (255,255,255))
    pantalla.blit(texto, (10, 10))  # posición arriba a la izquierda


    pygame.display.flip()
    clock.tick(10)

pygame.quit()
