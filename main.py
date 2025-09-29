import pygame
from config import ANCHO, ALTO, BASE, DEPOSITO, VELOCIDAD
from mapa import generar_mapa
from escenario import Escenario
from Agente.AgenteIA import AgenteIA

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))# ventana
pygame.display.set_caption("Bomberman Grid Movement")#titulo

# --- Instancias ---

# Lista de posiciones (fila, col)
deposito=(1, 8)
mapa = generar_mapa(num_ratones=10, num_obstaculos=20)
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
    escenario.actualizar_items()
    escenario.dibujar(pantalla)
    #jugador.dibujar(pantalla)
    ia.dibujar(pantalla)
    pygame.display.flip()
    clock.tick(VELOCIDAD)

pygame.quit()