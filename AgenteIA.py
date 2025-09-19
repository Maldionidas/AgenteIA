import pygame
from collections import deque
from config import TAM
from bomba import Bomba

COOL_DOWN_BOMBA = 2000  # ms de espera entre bombas

class AgenteIA:
    def __init__(self, fila, col, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM//3
        self.ruta = []          # ruta hacia la caja
        self.objetivo = None    # celda de la caja actual
        self.bomba_activa = False
        
        

    def bfs(self, mapa, start, goals, bombas):
        """BFS para encontrar ruta corta evitando muros y bombas activas"""
        queue = deque()
        queue.append((start, []))
        visitados = set()
        visitados.add(start)
        while queue:
            (f, c), path = queue.popleft()
            if (f, c) in goals:
                return path
            for df, dc, accion in [(1,0,"abajo"),(-1,0,"arriba"),(0,1,"derecha"),(0,-1,"izquierda")]:
                nf, nc = f+df, c+dc
                if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                    # Evitar muros y celdas con bomba
                    if mapa[nf][nc] != 1 and not any(b.celda==(nf,nc) and not b.exploto for b in bombas):
                        if (nf,nc) not in visitados:
                            visitados.add((nf,nc))
                            queue.append(((nf,nc), path+[accion]))
        return []

    def actualizar(self, mapa, bombas, ahora):
        # Si la bomba sigue activa, no buscar nueva caja
        if self.bomba_activa:
            if not any(b.celda==(self.fila,self.col) and not b.exploto for b in bombas):
                self.bomba_activa = False
            else:
                return  # espera a que explote la bomba

        # Si no hay objetivo o fue destruido, buscar nueva caja
        if not self.objetivo or mapa[self.objetivo[0]][self.objetivo[1]] != 2:
            # Lista de todas las cajas
            cajas = [(f,c) for f in range(len(mapa)) for c in range(len(mapa[0])) if mapa[f][c]==2]
            if cajas:
                self.objetivo = min(cajas, key=lambda pos: abs(pos[0]-self.fila)+abs(pos[1]-self.col))
                self.ruta = self.bfs(mapa, (self.fila,self.col), [self.objetivo], bombas)

        # Mover según la ruta
        if self.ruta:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

        # Si llegó a celda adyacente, colocar bomba
        if self.objetivo and abs(self.fila-self.objetivo[0])+abs(self.col-self.objetivo[1])==1:
            celda = (self.fila,self.col)
            if not any(b.celda==celda and not b.exploto for b in bombas):
                bombas.append(Bomba(celda, ahora))
                self.bomba_activa = True

    def mover(self, accion, mapa):
        if accion == "arriba" and self.fila > 0 and mapa[self.fila-1][self.col] != 1:
            self.fila -= 1
        elif accion == "abajo" and self.fila < len(mapa)-1 and mapa[self.fila+1][self.col] != 1:
            self.fila += 1
        elif accion == "izquierda" and self.col > 0 and mapa[self.fila][self.col-1] != 1:
            self.col -= 1
        elif accion == "derecha" and self.col < len(mapa[0])-1 and mapa[self.fila][self.col+1] != 1:
            self.col += 1

    def dibujar(self, pantalla):
        x = self.col*TAM + TAM//2
        y = self.fila*TAM + TAM//2
        pygame.draw.circle(pantalla, self.color, (x, y), self.radio)
