import pygame
from collections import deque
from config import TAM
from config import FILAS, COLS, CELDA_MURO, CELDA_PELOTA, CELDA_VACIA

COOL_DOWN_BOMBA = 2000  # ms de espera entre bombas

class AgenteIA:
    def __init__(self, fila, col, base, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3
        self.ruta = []          # ruta hacia la caja
        self.objetivo = None    # celda de la caja actual
        self.recolectadas = 0
        self.cargando = False
        self.base = base

        # === PASO 1: cargar sprites del gato y dejarlos a tamaño de celda ===
        # Asegúrate de haber generado cat_front.png, cat_back.png, cat_left.png, cat_right.png
        self.images = {
            "front": pygame.image.load("personajes/cat_front.png").convert_alpha(),
            "back":  pygame.image.load("personajes/cat_back.png").convert_alpha(),
            "left":  pygame.image.load("personajes/cat_left.png").convert_alpha(),
            "right": pygame.image.load("personajes/cat_right.png").convert_alpha(),
        }
        for k, img in self.images.items():
            self.images[k] = pygame.transform.scale(img, (TAM, TAM))
        self.dir = "front"

    def bfs(self, mapa, start, goals):
        """BFS para encontrar ruta corta evitando muros y bombas activas"""
        queue = deque()
        queue.append((start, []))
        visitados = set([start])
        
        while queue:
            (f, c), path = queue.popleft()
            if (f, c) in goals:
                return path
            for df, dc, accion in [(1,0,"abajo"),(-1,0,"arriba"),(0,1,"derecha"),(0,-1,"izquierda")]:
                nf, nc = f+df, c+dc
                if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                    # Evitar muros y celdas con bomba
                    if mapa[nf][nc] != 1 and (nf, nc) not in visitados:  # evita muros
                        visitados.add((nf, nc))
                        queue.append(((nf, nc), path+[accion]))
        return []

    def actualizar(self, mapa):
        # Si no hay objetivo o ya fue recogido, buscar otro
        if not self.cargando:
            if not self.objetivo or mapa[self.objetivo[0]][self.objetivo[1]] != 2:
                pelotas = [(f,c) for f in range(len(mapa)) for c in range(len(mapa[0])) if mapa[f][c] == 2]
                if pelotas:
                    self.objetivo = min(pelotas, key=lambda pos: abs(pos[0]-self.fila)+abs(pos[1]-self.col))
                    self.ruta = self.bfs(mapa, (self.fila, self.col), [self.objetivo])
        #si ya lleva pelota objetivo es la base
        else:
            if self.objetivo != self.base:
                self.objetivo = self.base
                self.ruta = self.bfs(mapa, (self.fila, self.col), [self.objetivo])
            
        # Mover según la ruta
        if self.ruta:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

        # Si llegó a la pelota → recogerla
        if self.objetivo and (self.fila, self.col) == self.objetivo:
            mapa[self.fila][self.col] = 0
            self.recolectadas += 1
            self.objetivo = None
            self.ruta = []

    def mover(self, accion, mapa):
        df, dc = 0, 0
        if accion == "arriba":
            df = -1
            self.dir = "back"
        elif accion == "abajo":
            df = 1
            self.dir = "front"
        elif accion == "izquierda":
            dc = -1
            self.dir = "left"
        elif accion == "derecha":
            dc = 1
            self.dir = "right"

        nueva_fila = self.fila + df
        nueva_col = self.col + dc

        if 0 <= nueva_fila < FILAS and 0 <= nueva_col < COLS:
            if mapa[nueva_fila][nueva_col] != 1:  # no muro
                self.fila = nueva_fila
                self.col = nueva_col

                # recoger pelota
                if mapa[self.fila][self.col] == 2 and not self.cargando:
                    self.cargando = True
                    mapa[self.fila][self.col] = 0

                # soltar en la base
                if (self.fila, self.col) == self.base and self.cargando:
                    print("Pelota entregada a la base!")
                    self.cargando = False
                    self.recolectadas += 1
                    self.objetivo = None
                    self.ruta = []

    def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        # blitea el sprite correcto según la dirección
        pantalla.blit(self.images[self.dir], (x, y))
