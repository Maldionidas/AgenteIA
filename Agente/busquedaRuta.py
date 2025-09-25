
import heapq
from config import CELDA_MURO
# ---------------- Dijkstra ----------------
def dijkstra( mapa, start, goals):
    pq = [(0, start, [])]  # (costo acumulado, nodo, path)
    dist = {start: 0}

    while pq:
        costo, (f, c), path = heapq.heappop(pq)

        if (f, c) in goals:
            return path

        if costo > dist[(f, c)]:
            continue

        for df, dc, accion in [(1,0,"abajo"), (-1,0,"arriba"), (0,1,"derecha"), (0,-1,"izquierda")]:
            nf, nc = f + df, c + dc
            if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                if mapa[nf][nc] != CELDA_MURO:
                    nuevo_costo = costo + 1
                    if (nf, nc) not in dist or nuevo_costo < dist[(nf, nc)]:
                        dist[(nf, nc)] = nuevo_costo
                        heapq.heappush(pq, (nuevo_costo, (nf, nc), path + [accion]))
    return []