import pygame
from collections import deque
from config import TAM, FILAS, COLS, CELDA_MURO, CELDA_PELOTA, CELDA_VACIA

class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3

        self.ruta = []              # pasos pendientes (acciones)
        self.objetivo = None        # celda objetivo actual
        self.cargando = False       # trae un ratón (solo de pelota -> depósito)
        self.fue_deposito = False   # acaba de depositar y debe ir a base
        self.contador_deposito = 0  # cuántos dejó en depósito
        self.recolectadas = 0       # cuántos contabilizados en base
        self.recargando = False

        self.font = pygame.font.SysFont(None, max(14, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        self.recarga_por_segundo = 10   # cuánto sube por segundo
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

        # ---------------- ENERGÍA (NUEVO) ----------------
        # Suficiente para recorrer el contorno del mapa (~perímetro en pasos)
        self.energia_max = 4 * (FILAS + COLS)
        self.energia = self.energia_max
        self.costo_paso = 1  # energía por cada cuadro recorrido

    # ---------------- BFS ----------------
    def bfs(self, mapa, start, goals):
        """Ruta (lista de acciones) desde start a cualquiera en goals evitando muros."""
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
        self.ruta = self.bfs(mapa, (self.fila, self.col), [destino]) or []

    def pelota_mas_cercana(self, mapa):
        """Pelota alcanzable más cercana por longitud de ruta."""
        pelotas = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_PELOTA]
        mejor = None
        mejor_len = None
        for p in pelotas:
            r = self.bfs(mapa, (self.fila, self.col), [p])
            if r:
                if mejor is None or len(r) < mejor_len:
                    mejor = p
                    mejor_len = len(r)
        return mejor

    # --------------- Lógica principal ---------------
    def actualizar(self, mapa):
        """
        Flujo:
        - Si NO cargando y NO viene de depósito: busca pelota; al pisarla, toma y va al depósito.
        - Al pisar depósito: suelta (cargando=False, fue_deposito=True, contador_deposito++) y va a base.
        - Al pisar base con fue_deposito=True: recolectadas++, fue_deposito=False, vuelve a buscar pelota.
        """
        # Recarga al pisar base (ahora gradual)
        # ----------------- RECARGA ESTRATÉGICA -----------------
        if (self.fila, self.col) == self.base:
            pelotas = [(f,c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_PELOTA]
            n_restantes = len(pelotas)

            if n_restantes > 0:
                if n_restantes >= 4:
                    objetivo_carga = self.energia_max   # FULL si hay muchos ratones
                else:
                    destino = self.pelota_mas_cercana(mapa)
                    if destino:
                        ruta_pelota = self.bfs(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo   = self.bfs(mapa, destino, [self.deposito]) or []
                        ruta_base   = self.bfs(mapa, self.deposito, [self.base]) or []
                        costo_ciclo = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)
                        objetivo_carga = min(self.energia_max, int(costo_ciclo * n_restantes * 1.2))
                    else:
                        objetivo_carga = self.energia_max
            else:
                objetivo_carga = self.energia_max

            # si aún no llega al objetivo, quedarse recargando
            if self.energia < objetivo_carga:
                self.recargando = True
                ahora = pygame.time.get_ticks()
                delta_ms = ahora - self.ultimo_tick
                recarga = (delta_ms / 1000) * self.recarga_por_segundo
                self.energia = min(objetivo_carga, self.energia + recarga)
                self.ultimo_tick = ahora
                return  # 👈 importantísimo: no hace nada más, se queda quieto cargando
            else:
                self.recargando = False
        # --------------------------------------------------------

        self.ultimo_tick = pygame.time.get_ticks()
        # --------------------------------------------------------

        # 1) Si llega a la base después de haber depositado (ya sin cargar)
        if not self.cargando and self.fue_deposito and (self.fila, self.col) == self.base:
            self.recolectadas += 1
            self.fue_deposito = False
            self.objetivo = None
            self.ruta = []

        # 2) Recoger pelota SOLO si NO está cargando y NO viene de depósito
        if not self.cargando and not self.fue_deposito:
            if mapa[self.fila][self.col] == CELDA_PELOTA:
                mapa[self.fila][self.col] = CELDA_VACIA
                self.cargando = True
                self.objetivo = None
                self.ruta = []
                # al recoger, su destino inmediato es el depósito
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)

        # 3) Si está cargando y pisa depósito -> soltar y luego ir a base
        if self.cargando and (self.fila, self.col) == self.deposito:
            # Soltar ratón
            self.cargando = False
            self.contador_deposito += 1
            self.objetivo = None
            self.ruta = []

            # Decidir si ir por otro ratón o recargar
            destino = self.pelota_mas_cercana(mapa)
            if destino:
                ruta_pelota = self.bfs(mapa, (self.fila, self.col), [destino])
                ruta_depo   = self.bfs(mapa, destino, [self.deposito]) if ruta_pelota else []
                ruta_base   = self.bfs(mapa, self.deposito, [self.base]) if ruta_depo else []
                costo_total = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)

                if self.energia >= int(costo_total * 1.2):
                    # Sí alcanza para otro ciclo → ir a por un nuevo ratón
                    self._ruta_hacia(mapa, destino)
                else:
                    # No alcanza → mejor recargar
                    self._ruta_hacia(mapa, self.base)
            else:
                # No hay ratones → a recargar
                self._ruta_hacia(mapa, self.base)

       # ---------- NUEVO BLOQUE: decidir si buscar ratón o recargar ----------
        if not self.ruta:
            if self.cargando:
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)
            else:
                if self.fue_deposito:
                    self._ruta_hacia(mapa, self.base)
                else:
                    destino = self.pelota_mas_cercana(mapa)
                    if destino:
                        ruta_pelota = self.bfs(mapa, (self.fila, self.col), [destino])
                        ruta_depo   = self.bfs(mapa, destino, [self.deposito]) if ruta_pelota else []
                        ruta_base   = self.bfs(mapa, self.deposito, [self.base]) if ruta_depo else []
                        
                        costo_total = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)
                        
                        # 🔋 Decisión: ¿alcanza la pila?
                        if self.energia >= int(costo_total * 1.2):
                            self._ruta_hacia(mapa, destino)
                        else:
                            # No alcanza, mejor va directo a base
                            self._ruta_hacia(mapa, self.base)
                    else:
                        self.objetivo = None  # idle si no hay pelotas
    # ---------------------------------------------------------------------

        # 5) Avanzar un paso
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
            # ↓↓↓ ENERGÍA por paso (sin bloquear movimiento si se agota)
            if self.energia > 0:
                self.energia = max(0, self.energia - self.costo_paso)
        # recoger/soltar/base se maneja en actualizar()

    # --------------- Render ---------------
    def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        pantalla.blit(self.images[self.dir], (x, y))

        # Solo mostrar ratón en la espalda cuando va cargando (hacia depósito)
        if self.cargando:
            img_w, img_h = self.raton_img.get_size()
            offset_x = (TAM - img_w) // 2
            offset_y = (TAM - img_h) // 2 - 6
            pantalla.blit(self.raton_img, (x + offset_x, y + offset_y))

        # (Opcional) contador visual en el depósito
        dx = self.deposito[1] * TAM
        dy = self.deposito[0] * TAM
        label = self.font.render(str(self.contador_deposito), True, (255, 255, 255))
        bg = label.get_rect()
        bg.topright = (dx + TAM - 3, dy + 3)
        bg.inflate_ip(6, 2)
        pygame.draw.rect(pantalla, (0, 0, 0), bg)
        pantalla.blit(label, (bg.right - label.get_width() - 3, bg.top + 1))

        # ---------------- BARRA DE ENERGÍA (HUD) ----------------
        # Fondo y marco
        hud_x, hud_y = 8, 8
        bar_w, bar_h = 150, 10
        pygame.draw.rect(pantalla, (60, 60, 60), (hud_x - 2, hud_y - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(pantalla, (30, 30, 30), (hud_x, hud_y, bar_w, bar_h))
        # Barra de energía proporcional
        pct = 0 if self.energia_max == 0 else self.energia / self.energia_max
        pygame.draw.rect(pantalla, (50, 200, 50), (hud_x, hud_y, int(bar_w * pct), bar_h))
        # Texto
        txt = self.font.render("ENERGIA", True, (255, 255, 255))
        pantalla.blit(txt, (hud_x, hud_y + bar_h + 4))
