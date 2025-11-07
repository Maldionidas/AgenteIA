# Agente/geneticAlg.py
from typing import List, Tuple
from config import (
    GA_PARAMS, ENERGY_PER_STEP_EMPTY, ENERGY_PER_STEP_CARRY,
    FILAS, COLS, COSTOS, CELDA_MURO,
)
from path_planning.ag_planner import GAPathPlanner

_DIRS = {"arriba":(-1,0),"abajo":(1,0),"izquierda":(0,-1),"derecha":(0,1)}
_DIRS_REV = {v:k for k,v in _DIRS.items()}

def _cells_to_actions(cells: List[Tuple[int,int]]) -> List[str]:
    if not cells: return []
    acc=[]
    for (r0,c0),(r1,c1) in zip(cells,cells[1:]):
        a=_DIRS_REV.get((r1-r0,c1-c0))
        if a: acc.append(a)
    return acc

def _cost_from_cells(grid, cells):
    total=0.0
    for (r,c) in cells[1:]:
        if 0<=r<FILAS and 0<=c<COLS: total+=COSTOS.get(grid[r][c],1)
        else: total+=1e9
    return total

def _ga_route_cells(grid,start,goal,mode,energia_restante,cargando):
    planner=GAPathPlanner(**GA_PARAMS)
    eps=ENERGY_PER_STEP_CARRY if cargando else ENERGY_PER_STEP_EMPTY
#    return planner.plan(grid,start,goal,mode.upper(),energia_restante,eps,True)
    cells = planner.plan(grid,start,goal,mode.upper(),energia_restante,eps,True)
    # Fallback: si GA no propone nada útil, da un paso "avaro" hacia el objetivo
    if len(cells) < 2:
        sr, sc = start
        gr, gc = goal
        candidatos = [ (sr-1,sc), (sr+1,sc), (sr,sc-1), (sr,sc+1) ]
        # ordena vecinos por Manhattan al objetivo, filtrando muros/bordes
        def inside(r,c): return 0 <= r < FILAS and 0 <= c < COLS
        vecinos = [(r,c) for (r,c) in candidatos if inside(r,c) and grid[r][c] != CELDA_MURO]
        if vecinos:
            vecinos.sort(key=lambda rc: abs(rc[0]-gr)+abs(rc[1]-gc))
            best = vecinos[0]
            cells = [start, best]
    return cells


def genetic_route(grid,start,goal,mode,energia_restante,cargando)->List[str]:
    return _cells_to_actions(_ga_route_cells(grid,start,goal,mode,energia_restante,cargando))

def genetic_shortest(grid,start,goals)->List[str]:
    if not goals: return []
    cells=_ga_route_cells(grid,start,goals[0],"REST",1e9,False)
    return _cells_to_actions(cells)

def genetic_cost(grid,start,goals):
    if not goals: return [], float("inf")
    cells=_ga_route_cells(grid,start,goals[0],"REST",1e9,False)
    return _cells_to_actions(cells), _cost_from_cells(grid, cells)






'''import heapq
from heapq import heappush, heappop
from config import FILAS, COLS, COSTOS, CELDA_MURO

# ---------------- Dijkstra (compat) -> devuelve solo ruta ----------------
def dijkstra(mapa, start, goals):
    fila, col = start
    prev = {}
    dist = {start: 0}
    pq = [(0, start)]  # (costo acumulado, nodo)

    while pq:
        d, (f, c) = heappop(pq)
        if (f, c) in goals:
            return reconstruir_camino(prev, start, (f, c))

        for df, dc, accion in [(-1,0,"arriba"), (1,0,"abajo"), (0,-1,"izquierda"), (0,1,"derecha")]:
            nf, nc = f + df, c + dc
            if 0 <= nf < FILAS and 0 <= nc < COLS:
                celda = mapa[nf][nc]
                costo = COSTOS.get(celda, 1)
                if costo == float("inf"):
                    continue
                nd = d + costo
                if (nf, nc) not in dist or nd < dist[(nf, nc)]:
                    dist[(nf, nc)] = nd
                    prev[(nf, nc)] = ((f, c), accion)
                    heappush(pq, (nd, (nf, nc)))
    return None

# ---------------- Dijkstra con costo total -> (ruta, costo) --------------
def dijkstra_con_costo(mapa, start, goals):
    fila, col = start
    prev = {}
    dist = {start: 0}
    pq = [(0, start)]  # (costo acumulado, nodo)

    while pq:
        d, (f, c) = heappop(pq)
        if (f, c) in goals:
            ruta = reconstruir_camino(prev, start, (f, c))
            return ruta, d

        for df, dc, accion in [(-1,0,"arriba"), (1,0,"abajo"), (0,-1,"izquierda"), (0,1,"derecha")]:
            nf, nc = f + df, c + dc
            if 0 <= nf < FILAS and 0 <= nc < COLS:
                celda = mapa[nf][nc]
                costo = COSTOS.get(celda, 1)
                if costo == float("inf"):
                    continue
                nd = d + costo
                if (nf, nc) not in dist or nd < dist[(nf, nc)]:
                    dist[(nf, nc)] = nd
                    prev[(nf, nc)] = ((f, c), accion)
                    heappush(pq, (nd, (nf, nc)))
    return None, float("inf")

def reconstruir_camino(prev, inicio, goal):
    ruta = []
    nodo = goal
    while nodo != inicio:
        nodo_prev, accion = prev[nodo]
        ruta.append(accion)
        nodo = nodo_prev
    ruta.reverse()
    return ruta
'''