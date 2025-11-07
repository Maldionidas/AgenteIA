# Agente/path_planning/ga_planner.py
from __future__ import annotations
import random
from typing import List, Tuple, Optional, Literal, Dict
from config import CELDA_MURO, FILAS, COLS, COSTOS
from collections import Counter

Move = Tuple[int, int]  # delta fila/col
MOVES: List[Move] = [(-1,0),(1,0),(0,-1),(0,1)]  # ↑ ↓ ← →

Mode = Literal["HUNT", "CARRY", "REST"]

class GAPathPlanner:
    """
    Planificador por Algoritmo Genético.
    Decodifica un cromosoma (secuencia de movimientos) en una ruta de celdas.
    Fitness multi-criterio según el modo:
      - HUNT: acercarse/atrapar ratón móvil (snapshot actual).
      - CARRY: llegar a caja.
      - REST: llegar a base.
    Soporta restricción de energía como penalización dura.
    """
    def __init__(self, **hp):
        self.max_steps   = int(hp.get("max_steps", 120))
        self.pop_size    = int(hp.get("pop_size", 80))
        self.generations = int(hp.get("generations", 80))
        self.p_crossover = float(hp.get("p_crossover", 0.9))
        self.p_mutation  = float(hp.get("p_mutation", 0.08))
        self.tourn_k     = int(hp.get("tourn_k", 3))
        self.wall_penalty= float(hp.get("wall_penalty", 1000.0))
        self.step_cost   = float(hp.get("step_cost", 1.0))
        self.turn_cost   = float(hp.get("turn_cost", 0.2))
        self.catch_bonus = float(hp.get("catch_bonus", 1_000_000.0))
        self.deliver_bonus = float(hp.get("deliver_bonus", 1_000_000.0))
        self.terrain_w   = float(hp.get("terrain_cost_w", 1.0))

    # ========= API principal =========
    def plan(self,
             grid: List[List[int]],
             start: Tuple[int,int],
             goal: Tuple[int,int],
             mode: Mode,
             energy_left: Optional[float] = None,
             energy_per_step: Optional[float] = None,
             must_be_feasible: bool = True
            ) -> List[Tuple[int,int]]:
        """
        Retorna una ruta [(r,c), ...] a partir de un GA de horizonte.
        - grid: matriz de celdas (0=libre, 1=muro) o ajusta en _is_free.
        - start: (fila, col) del gato.
        - goal:  objetivo del modo (ratón para HUNT, caja para CARRY, base para REST).
        - mode:  "HUNT" | "CARRY" | "REST"
        - energy_left: energía restante del gato (si la controlas aquí).
        - energy_per_step: coste por paso relativo al modo.
        - must_be_feasible: si True, rutas que no alcancen con energía reciben gran penalización.
        """
        # horizonte dinámico según distancia
        base_h = abs(start[0]-goal[0]) + abs(start[1]-goal[1])
        H = max(4, int(base_h * 1.25))                 # 25% de holgura
        pop = [self._rand_individual(H) for _ in range(self.pop_size)]
        
        best_ind, best_fit = None, float("inf")

        for _ in range(self.generations):
            fits = [self._fitness(grid, start, goal, mode, ind,
                                  energy_left, energy_per_step, must_be_feasible)
                    for ind in pop]

            for ind, f in zip(pop, fits):
                if f < best_fit:
                    best_fit, best_ind = f, ind[:]

            # paro temprano: si el mejor ya alcanza el objetivo
            if best_ind and self._reaches(grid, start, goal, mode, best_ind):
                break

            # selección torneo
            parents = [self._tournament(pop, fits) for _ in range(self.pop_size)]

            # cruce + mutación
            next_pop = []
            for i in range(0, self.pop_size, 2):
                p1 = parents[i]
                p2 = parents[(i+1) % self.pop_size]
                c1, c2 = self._crossover(p1, p2) if random.random() < self.p_crossover else (p1[:], p2[:])
                self._mutate(c1)
                self._mutate(c2)
                next_pop.extend([c1, c2])
            pop = next_pop[:self.pop_size]

        # decodifica cromosoma mejor → ruta
        return self._decode_route(start, best_ind or [], grid, goal)

    # ========= helpers GA =========
    def _rand_individual(self, length: int) -> List[int]:
        return [random.randrange(4) for _ in range(length)]

    def _decode_route(self, start, genes, grid, goal = None) -> List[Tuple[int,int]]:
        r, c = start
        path = [(r, c)]
        for g in genes:
            dr, dc = MOVES[g]
            nr, nc = r + dr, c + dc
            if not self._is_free(grid, nr, nc):
                nr, nc = r, c
            if (nr, nc) != (r, c):
                path.append((nr, nc))
            r, c = nr, nc
            if goal and (r,c) == goal:
                break
        # quita repeticiones consecutivas
        pruned = [path[0]]
        for cell in path[1:]:
            if cell != pruned[-1]:
                pruned.append(cell)
        return pruned

    def _simulate(self, grid, start, genes, goal):
        r, c = start
        prev_move = None
        turns = 0
        collisions = 0
        terrain_cost = 0.0
        visited = [(r,c)]
        progress_gain = 0.0
        prev_d = abs(r-goal[0]) + abs(c-goal[1])
        for g in genes:
            dr, dc = MOVES[g]
            nr, nc = r + dr, c + dc
            if not self._is_free(grid, nr, nc):
                collisions += 1
                nr, nc = r, c
            else:
                # sólo sumamos costo de terreno si realmente avanzamos de celda
                if 0 <= nr < FILAS and 0 <= nc < COLS:
                    terrain_cost += float(COSTOS.get(grid[nr][nc], 1))
            d = abs(nr-goal[0]) + abs(nc-goal[1])
            progress_gain += (prev_d - d)
            prev_d = d
            
            if prev_move and prev_move != (dr, dc):
                turns += 1
            r, c = nr, nc
            prev_move = (dr, dc)
            visited.append((r, c))
        counts = Counter(visited)
        repeats = sum(max(0, k-1) for k in counts.values())
        return (r, c), collisions, turns, terrain_cost, progress_gain, repeats

    def _fitness(self, grid, start, goal, mode, genes,
                 energy_left, energy_per_step, must_be_feasible) -> float:
        (r, c), collisions, turns, terrain_cost, progress_gain, repeats = self._simulate(grid, start, genes, goal)
        manhattan = abs(r - goal[0]) + abs(c - goal[1])

        # costo base: pasos + giros + colisiones + distancia + terreno
        base = (
            (len(genes) * self.step_cost)
            + (collisions * self.wall_penalty)
            + (turns * self.turn_cost)
            + manhattan
            + self.terrain_w * terrain_cost
        )
        # premia progreso acumulado (me acerqué muchas veces)
        base -= 1.5 * progress_gain
        # penaliza bucles
        base += 2.0 * repeats
        # bonificaciones por logro de objetivo según modo
        reached = (r, c) == goal
        if mode == "HUNT":
            if reached:
                base -= self.catch_bonus
        elif mode in ("CARRY", "REST"):
            if reached:
                base -= self.deliver_bonus

        # factibilidad energética (opcional dura)
        if must_be_feasible and energy_left is not None and energy_per_step is not None:
            needed = len(genes) * energy_per_step
            if needed > energy_left:
                # gran penalización si la ruta propuesta no cabe en energía
                base += (needed - energy_left) * self.wall_penalty

        return base

    def _reaches(self, grid, start, goal, mode, genes) -> bool:
        (r, c), *_ = self._simulate(grid, start, genes, goal)
        return (r, c) == goal


    def _tournament(self, pop, fits) -> List[int]:
        best_i = None
        for _ in range(self.tourn_k):
            i = random.randrange(len(pop))
            if best_i is None or fits[i] < fits[best_i]:
                best_i = i
        return pop[best_i][:]

    def _crossover(self, a, b):
        cut = random.randrange(1, len(a))
        return a[:cut] + b[cut:], b[:cut] + a[cut:]

    def _mutate(self, ind):
        for i in range(len(ind)):
            if random.random() < self.p_mutation:
                ind[i] = random.randrange(4)

    def _is_free(self, grid, r, c) -> bool:
        if r < 0 or c < 0:
            return False
        try:
            return grid[r][c] != CELDA_MURO  # libre si NO es muro
        except IndexError:
            return False