import pygame
from config import *
#Clase Bomba
class Bomba:
    def __init__(self, celda, t_colocada):
        #posicion de la bomba en celdas (fila, columna)
        self.celda = celda
        #empieza el temporizador de la bomba
        self.t_colocada = t_colocada
        #estado de la bomba, si exploto o no
        self.exploto = False
        #tiempo de la explosion, para saber cuando dibujar las llamas
        self.t_explosion = None
        self.llamas = []
    #determina si la bomba debe explotar
    def deberia_explotar(self, ahora):
        return (not self.exploto) and (ahora - self.t_colocada >= FUSIBLE_MS)
    #para dibujar las llamas, se guarda en una lista las celdas que deben ser afectadas por la explosion
    def explotar(self, mapa):
        self.exploto = True
        self.t_explosion = pygame.time.get_ticks()
        #celda de la bomba
        f0, c0 = self.celda
        #incluir la celda de la bomba
        self.llamas = [(f0, c0)]
        #explosion en las 4 direcciones
        for df, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            #para cada paso en el alcance de la llama
            for paso in range(1, ALCANCE_LLAMA+1):
                f = f0 + df*paso
                c = c0 + dc*paso
                #verifica si la celda esta dentro del mapa
                if not (0 <= f < FILAS and 0 <= c < COLS):
                    break
                #si encuentra un muro, se detiene
                if mapa[f][c] == CELDA_MURO:
                    break
                self.llamas.append((f, c))
                #si encuentra un muro destruible, lo destruye y se detiene
                if mapa[f][c] == CELDA_DESTRUIBLE:
                    mapa[f][c] = CELDA_VACIA
                    break
#verifica si las llamas siguen activas
    def llamas_activas(self, ahora):
        return self.exploto and (ahora - self.t_explosion <= DURACION_LLAMA_MS)
#dibuja la bomba o las llamas si exploto
    def dibujar(self, pantalla, ahora):
        f, c = self.celda
        if not self.exploto:
            pygame.draw.circle(pantalla, BOMBA_COLOR,
                               (c*TAM + TAM//2, f*TAM + TAM//2), TAM//3)
        elif self.llamas_activas(ahora):
            for f, c in self.llamas:
                pygame.draw.rect(pantalla, LLAMA_COLOR,
                                 (c*TAM, f*TAM, TAM, TAM))