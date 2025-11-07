# Agente/path_planning/base.py
from typing import List, Tuple

class PathPlanner:
    def plan(self, grid, start: Tuple[int,int], goal: Tuple[int,int]) -> List[Tuple[int,int]]:
        """Retorna lista de celdas (fila, col) desde start al goal."""
        raise NotImplementedError
