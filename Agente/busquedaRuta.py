
import heapq
from heapq import heappush, heappop
from config import FILAS, COLS, COSTOS, CELDA_MURO
# ---------------- Dijkstra ----------------
def dijkstra( mapa, start, goals):
    fila, col = start
    dist = { start: 0 }
    prev = {}
    pq = [(0, start)]  # (costo acumulado, nodo)
    dist = {start: 0}

    while pq:
        d, (f, c) = heappop(pq)

        if (f, c) in goals:
            return reconstruir_camino(prev, start, (f, c))


        # Explorar vecinos
        for df, dc, accion in [(-1,0,"arriba"), (1,0,"abajo"), (0,-1,"izquierda"), (0,1,"derecha")]:
            nf, nc = f + df, c + dc
            if 0 <= nf < FILAS and 0 <= nc < COLS:
                celda = mapa[nf][nc]
                costo = COSTOS.get(celda, 1)  # valor según terreno
                if costo == float("inf"):
                    continue  # muro o impasable
                nd = d + costo
                if (nf, nc) not in dist or nd < dist[(nf, nc)]:
                    dist[(nf, nc)] = nd
                    prev[(nf, nc)] = ((f, c), accion)
                    heappush(pq, (nd, (nf, nc)))
    return None  # no hay camino

def reconstruir_camino(prev, inicio, goal):
    ruta = []
    nodo = goal
    while nodo != inicio:
        nodo_prev, accion = prev[nodo]
        ruta.append(accion)
        nodo = nodo_prev
    ruta.reverse()
    return ruta