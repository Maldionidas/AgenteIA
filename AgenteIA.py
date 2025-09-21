import pygame
from collections import deque
from config import TAM, FILAS, COLS, CELDA_MURO, CELDA_PELOTA, CELDA_VACIA

COOL_DOWN_BOMBA = 2000  # ms de espera entre bombas

class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3

        self.ruta = []            # pasos pendientes (acciones) hacia objetivo
        self.objetivo = None      # celda objetivo actual (tupla)
        self.cargando = False     # si trae un ratón
        self.fue_deposito = False # ya pasó por el depósito en este ciclo
        self.recolectadas = 0     # entregadas en base
        self.contador_deposito = 0
        self.font = pygame.font.SysFont(None, max(14, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        # Sprites del gato
        self.images = {
            "front": pygame.image.load("personajes/cat_front.png").convert_alpha(),
            "back":  pygame.image.load("personajes/cat_back.png").convert_alpha(),
            "left":  pygame.image.load("personajes/cat_left.png").convert_alpha(),
            "right": pygame.image.load("personajes/cat_right.png").convert_alpha(),
        }
        for k, img in self.images.items():
            self.images[k] = pygame.transform.scale(img, (TAM, TAM))
        self.dir = "front"

    # ---------------- BFS ----------------
    def bfs(self, mapa, start, goals):
        """Retorna la ruta (lista de acciones) desde start hasta cualquiera en goals evitando muros."""
        queue = deque()
        queue.append((start, []))
        visitados = set([start])

        while queue:
            (f, c), path = queue.popleft()
            if (f, c) in goals:
                return path
            for df, dc, accion in [(1,0,"abajo"),(-1,0,"arriba"),(0,1,"derecha"),(0,-1,"izquierda")]:
                nf, nc = f + df, c + dc
                if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                    if mapa[nf][nc] != CELDA_MURO and (nf, nc) not in visitados:
                        visitados.add((nf, nc))
                        queue.append(((nf, nc), path + [accion]))
        return []

    # --------------- Helpers ---------------
    def _ruta_hacia(self, mapa, destino):
        self.objetivo = destino
        self.ruta = self.bfs(mapa, (self.fila, self.col), [destino])

    def pelota_mas_cercana(self, mapa):
        """Busca la pelota alcanzable más cercana por BFS (por longitud de ruta)."""
        pelotas = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_PELOTA]
        mejor = None
        mejor_len = None
        for p in pelotas:
            r = self.bfs(mapa, (self.fila, self.col), [p])
            if r:  # solo consideramos alcanzables
                if mejor is None or len(r) < mejor_len:
                    mejor = p
                    mejor_len = len(r)
        return mejor

    # --------------- Lógica principal ---------------
    def actualizar(self, mapa):
        # Eventos por posición (más robusto que depender del objetivo actual):
        # 1) Si pisa una pelota y NO iba cargando -> recoger
        if not self.cargando and mapa[self.fila][self.col] == CELDA_PELOTA:
            mapa[self.fila][self.col] = CELDA_VACIA
            self.cargando = True
            self.fue_deposito = False
            self.objetivo = None
            self.ruta = []

        # 2) Si va cargando y pisa depósito y aún no había pasado -> marcar depósito
        if self.cargando and not self.fue_deposito and (self.fila, self.col) == self.deposito:
            # Aquí "deja" el ratón en la caja intermedia
            self.fue_deposito = True
            self.contador_deposito += 1
            self.objetivo = None
            self.ruta = []

        # 3) Si va cargando, ya pasó por depósito y pisa base -> entrega y resetea ciclo
        if self.cargando and self.fue_deposito and (self.fila, self.col) == self.base:
            self.cargando = False
            self.fue_deposito = False
            self.recolectadas += 1
            self.objetivo = None
            self.ruta = []

        # Decisión de objetivo si no hay ruta activa
        if not self.ruta:
            if not self.cargando:
                # Buscar siguiente pelota alcanzable
                destino = self.pelota_mas_cercana(mapa)
                if destino:
                    self._ruta_hacia(mapa, destino)
                else:
                    # No hay pelotas -> quedarse idle
                    self.objetivo = None
            else:
                # Va cargando: primero al depósito (si existe y no ha pasado), luego a la base
                if self.deposito and not self.fue_deposito:
                    self._ruta_hacia(mapa, self.deposito)
                else:
                    self._ruta_hacia(mapa, self.base)

        # Mover un paso si hay ruta
        if self.ruta:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

    # --------------- Movimiento ---------------
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

        nf = self.fila + df
        nc = self.col + dc
        if 0 <= nf < FILAS and 0 <= nc < COLS and mapa[nf][nc] != CELDA_MURO:
            self.fila, self.col = nf, nc
        # OJO: aquí NO recogemos ni entregamos; eso lo maneja actualizar()

    # --------------- Render ---------------
    def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        pantalla.blit(self.images[self.dir], (x, y))

        # contador visible en la celda del depósito (esquina sup. derecha)
        dx = self.deposito[1] * TAM
        dy = self.deposito[0] * TAM
        label = self.font.render(str(self.contador_deposito), True, (255, 255, 255))
        bg = label.get_rect()
        bg.topright = (dx + TAM - 3, dy + 3)
        bg.inflate_ip(6, 2)  # un poquito de margen

        pygame.draw.rect(pantalla, (0, 0, 0), bg)  # fondo negro
        pantalla.blit(label, (bg.right - label.get_width() - 3, bg.top + 1))
