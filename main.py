import time

import pygame
import random
from config import ANCHO, ALTO, FUENTE, BASE, DEPOSITO, VELOCIDAD
from mapa import generar_mapa
from escenario import Escenario
#from jugador import Jugador
#from bomba import Bomba
from AgenteIA import AgenteIA

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))# ventana
pygame.display.set_caption("Bomberman Grid Movement")#titulo

# --- Instancias ---

# Lista de posiciones (fila, col)
deposito=(1, 8)
mis_muros = [(2,2), (2,3), (3,2), (5,5), (6,6)]
mapa = generar_mapa(mis_muros, num_ratones=10)
escenario = Escenario(mapa, BASE, DEPOSITO)
#jugador = Jugador(1, 1)  # posición inicial del jugador
bombas = []  # lista de bombas
ia = AgenteIA(1, 1,BASE, DEPOSITO)  # por ejemplo, empieza abajo a la derecha



# --- Bucle principal ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    ahora = pygame.time.get_ticks()
    ia.actualizar(mapa)

    # sincroniza contadores con el escenario
    escenario.entregados_deposito = ia.contador_deposito
    escenario.entregados_base = ia.recolectadas

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
    
    # --- Dibujo ---
    pantalla.fill((0, 0, 0))
    escenario.dibujar(pantalla)
    #jugador.dibujar(pantalla)
    ia.dibujar(pantalla)
    pygame.display.flip()
    clock.tick(VELOCIDAD)

pygame.quit()


'''
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:  # colocar bomba
                if jugador.bombas_restantes > 0:
                    #celda = (jugador.fila, jugador.col)
                    #verifica si hay una bomba activa si hay, no puedes colocar otra
                    if not any(not b.exploto for b in bombas):
                        #saca la coordenada de el jugador
                        celda = (jugador.fila, jugador.col)
                        #dibuja la bomba y resta una bomba disponible
                        bombas.append(Bomba(celda, ahora))
                        jugador.bombas_restantes -= 1
                


    teclas = pygame.key.get_pressed()
    
    jugador.mover(teclas, mapa)
    
     # Recargar bombas si está en la base
    if jugador.fila == 1 and jugador.col == 1:
        jugador.bombas_restantes = jugador.max_bombas
    
    accion_ia = ia.decidir()
    ia.mover(accion_ia, mapa)
    ia.colocar_bomba(ahora, bombas)
    '''