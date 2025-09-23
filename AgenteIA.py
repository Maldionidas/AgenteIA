import pygame
import heapq
from config import TAM, FILAS, COLS, CELDA_MURO, CELDA_PELOTA, CELDA_VACIA

class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3

        self.ruta = []
        self.objetivo = None
        self.cargando = False
        self.fue_deposito = False
        self.contador_deposito = 0
        self.recolectadas = 0
        self.recargando = False

        # --- Animación de recoger ---
        self.animando = False
        self.inicio_animacion = 0
        self.tiempo_animacion = 1000  # 1 segundo en ms

        self.estado = "Idle"  # leyenda de estado

        self.font = pygame.font.SysFont(None, max(16, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        self.recarga_por_segundo = 10
        self.ultimo_tick = pygame.time.get_ticks()

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

        self.raton_img = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(self.raton_img, (raton_size, raton_size))

        # Energía
        self.energia_max = 4 * (FILAS + COLS)
        self.energia = self.energia_max
        self.costo_paso = 1

    # ---------------- Dijkstra ----------------
    def dijkstra(self, mapa, start, goals):
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

    # --------------- Helpers ---------------
    def _ruta_hacia(self, mapa, destino):
        self.objetivo = destino
        self.ruta = self.dijkstra(mapa, (self.fila, self.col), [destino]) or []

    def pelota_mas_cercana(self, mapa):
        pelotas = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_PELOTA]
        mejor = None
        mejor_len = None
        for p in pelotas:
            r = self.dijkstra(mapa, (self.fila, self.col), [p])
            if r:
                if mejor is None or len(r) < mejor_len:
                    mejor = p
                    mejor_len = len(r)
        return mejor

    # --------------- Lógica principal ---------------
    def actualizar(self, mapa):
        # --- Si se quedó sin energía ---
        if self.energia <= 0:
            self.estado = "Cansancio al límite"
            return

        # --- Si está en animación de recoger ---
        if self.animando:
            self.estado = "Recogiendo ratón"
            ahora = pygame.time.get_ticks()
            if ahora - self.inicio_animacion >= self.tiempo_animacion:
                self.animando = False
                self.cargando = True
                mapa[self.fila][self.col] = CELDA_VACIA
                self.estado = "Yendo a depositar ratón"
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)
            return

        # --- Recarga progresiva en base ---
        if (self.fila, self.col) == self.base:
            pelotas = [(f,c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_PELOTA]
            n_restantes = len(pelotas)

            if n_restantes > 0:
                if n_restantes >= 4:
                    objetivo_carga = self.energia_max
                else:
                    destino = self.pelota_mas_cercana(mapa)
                    if destino:
                        ruta_pelota = self.dijkstra(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo   = self.dijkstra(mapa, destino, [self.deposito]) or []
                        ruta_base   = self.dijkstra(mapa, self.deposito, [self.base]) or []
                        costo_ciclo = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)
                        objetivo_carga = min(self.energia_max, int(costo_ciclo * n_restantes * 1.2))
                    else:
                        objetivo_carga = self.energia_max
            else:
                objetivo_carga = self.energia_max

            if self.energia < objetivo_carga:
                self.estado = "Descansando"
                self.recargando = True
                ahora = pygame.time.get_ticks()
                delta_ms = ahora - self.ultimo_tick
                recarga = (delta_ms / 1000) * self.recarga_por_segundo
                self.energia = min(objetivo_carga, self.energia + recarga)
                self.ultimo_tick = ahora
                return
            else:
                self.recargando = False

        self.ultimo_tick = pygame.time.get_ticks()

        # --- Contabilizar al llegar a base tras depositar ---
        if not self.cargando and self.fue_deposito and (self.fila, self.col) == self.base:
            self.recolectadas += 1
            self.fue_deposito = False
            self.objetivo = None
            self.ruta = []

        # --- Al pisar una pelota: iniciar animación ---
        if not self.cargando and not self.fue_deposito:
            if mapa[self.fila][self.col] == CELDA_PELOTA:
                self.animando = True
                self.inicio_animacion = pygame.time.get_ticks()
                self.estado = "Recogiendo ratón"
                self.objetivo = None
                self.ruta = []
                return

        # --- Al llegar al depósito con un ratón ---
        if self.cargando and (self.fila, self.col) == self.deposito:
            self.cargando = False
            self.contador_deposito += 1
            self.objetivo = None
            self.ruta = []

            destino = self.pelota_mas_cercana(mapa)
            if destino:
                # rutas necesarias
                ruta_pelota = self.dijkstra(mapa, (self.fila, self.col), [destino]) or []
                ruta_depo   = self.dijkstra(mapa, destino, [self.deposito]) or []
                ruta_base   = self.dijkstra(mapa, self.deposito, [self.base]) or []

                costo_total = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)

                if self.energia >= int(costo_total * 1.1):
                    self.estado = "Buscando ratón"
                    self.fue_deposito = False
                    self._ruta_hacia(mapa, destino)
                else:
                    self.estado = "Cansancio al límite"
                    self.fue_deposito = True
                    self._ruta_hacia(mapa, self.base)
            else:
                self.estado = "Cansancio al límite"
                self.fue_deposito = True
                self._ruta_hacia(mapa, self.base)

        # --- Planear ruta cuando no hay ruta pendiente ---
        if not self.ruta:
            if self.cargando:
                self.estado = "Yendo a depositar ratón"
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)
            else:
                if self.fue_deposito:
                    self.estado = "Descansando"
                    self._ruta_hacia(mapa, self.base)
                else:
                    destino = self.pelota_mas_cercana(mapa)
                    if destino:
                        ruta_pelota = self.dijkstra(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo   = self.dijkstra(mapa, destino, [self.deposito]) or []
                        costo_hasta_depo = len(ruta_pelota) + len(ruta_depo)

                        if self.energia >= int(costo_hasta_depo * 1.1):
                            self.estado = "Buscando ratón"
                            self._ruta_hacia(mapa, destino)
                        else:
                            self.estado = "Cansancio al límite"
                            self._ruta_hacia(mapa, self.base)
                    else:
                        self.objetivo = None

        # --- Avanzar un paso ---
        if self.ruta:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

    # --------------- Movimiento ---------------
    def mover(self, accion, mapa):
        df, dc = 0, 0
        if accion == "arriba":
            df = -1; self.dir = "back"
        elif accion == "abajo":
            df = 1;  self.dir = "front"
        elif accion == "izquierda":
            dc = -1; self.dir = "left"
        elif accion == "derecha":
            dc = 1;  self.dir = "right"

        nf = self.fila + df
        nc = self.col + dc
        if 0 <= nf < FILAS and 0 <= nc < COLS and mapa[nf][nc] != CELDA_MURO:
            self.fila, self.col = nf, nc
            if self.energia > 0:
                self.energia = max(0, self.energia - self.costo_paso)

    # --------------- Render ---------------
    def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        pantalla.blit(self.images[self.dir], (x, y))

        if self.animando:
            img_w, img_h = self.raton_img.get_size()
            pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y - img_h//2))

        if self.cargando:
            img_w, img_h = self.raton_img.get_size()
            offset_x = (TAM - img_w) // 2
            offset_y = (TAM - img_h) // 2 - 6
            pantalla.blit(self.raton_img, (x + offset_x, y + offset_y))

        dx = self.deposito[1] * TAM
        dy = self.deposito[0] * TAM
        label = self.font.render(str(self.contador_deposito), True, (255, 255, 255))
        bg = label.get_rect()
        bg.topright = (dx + TAM - 3, dy + 3)
        bg.inflate_ip(6, 2)
        pygame.draw.rect(pantalla, (0, 0, 0), bg)
        pantalla.blit(label, (bg.right - label.get_width() - 3, bg.top + 1))

        hud_x, hud_y = 8, 8
        bar_w, bar_h = 150, 10
        pygame.draw.rect(pantalla, (60, 60, 60), (hud_x - 2, hud_y - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(pantalla, (30, 30, 30), (hud_x, hud_y, bar_w, bar_h))
        pct = 0 if self.energia_max == 0 else self.energia / self.energia_max
        pygame.draw.rect(pantalla, (50, 200, 50), (hud_x, hud_y, int(bar_w * pct), bar_h))
        txt = self.font.render("ENERGIA", True, (255, 255, 255))
        pantalla.blit(txt, (hud_x, hud_y + bar_h + 4))

        estado_txt = self.font.render(f"Estado: {self.estado}", True, (255, 255, 255))
        fondo = estado_txt.get_rect()
        fondo.midtop = (COLS * TAM // 2, 5)
        pygame.draw.rect(pantalla, (0, 0, 0), fondo.inflate(10, 6))
        pantalla.blit(estado_txt, estado_txt.get_rect(center=fondo.center))
