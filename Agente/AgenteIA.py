import pygame
from config import TAM, FILAS, COLS, CELDA_MURO, CELDA_RATON, CELDA_VACIA, COSTOS
from .busquedaRuta import dijkstra
from .energia import Energia
from .animaciones import Animaciones
from .render import dibujar
class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200,50,50)):
        self.fila = fila
        self.col = col
        self.color = color
        self.radio = TAM // 3
        ### --- Estados de ruta y objetivo ---
        self.ruta = []
        self.objetivo = None
        self.cargando = False
        self.fue_deposito = False
        self.contador_deposito = 0
        self.recolectadas = 0
        #self.recargando = False

        # --- Animación de recoger ---
        self.animando = False
        self.inicio_animacion = 0
        self.tiempo_animacion = 1000  # 1 segundo en ms
        self.estado = "Idle"  # leyenda de estado

        self.font = pygame.font.SysFont(None, max(16, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito
        
        # Energía
        self.energia = Energia(energia_max=200, recarga_por_segundo=10, costo_paso=1)


        

        # Sprites del gato
        self.images = {
            "front": pygame.image.load("AgenteIA/personajes/cat_front.png").convert_alpha(),
            "back":  pygame.image.load("AgenteIA/personajes/cat_back.png").convert_alpha(),
            "left":  pygame.image.load("AgenteIA/personajes/cat_left.png").convert_alpha(),
            "right": pygame.image.load("AgenteIA/personajes/cat_right.png").convert_alpha(),
        }
        for k, img in self.images.items():
            self.images[k] = pygame.transform.scale(img, (TAM, TAM))
        self.dir = "front"
        # Sprite del ratón
        self.raton_img = pygame.image.load("AgenteIA/personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(self.raton_img, (raton_size, raton_size))

    # --------------- Helpers ---------------
    def _ruta_hacia(self, mapa, destino):
        self.objetivo = destino
        self.ruta = dijkstra(mapa, (self.fila, self.col), [destino]) or []

    def raton_mas_cercano(self, mapa):
        ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
        mejor = None
        mejor_len = None
        for p in ratones:
            r = dijkstra(mapa, (self.fila, self.col), [p])
            if r:
                if mejor is None or len(r) < mejor_len:
                    mejor = p
                    mejor_len = len(r)
        return mejor

    # --------------- Lógica principal ---------------
    def actualizar(self, mapa):
        # --- Si se quedó sin energía ---
        if self.energia.valor <= 0:
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

        # --- Logica de la energia del agente ---
        if (self.fila, self.col) == self.base:
            ratones = [(f,c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
            n_restantes = len(ratones)

            if n_restantes > 0:
                if n_restantes >= 4:
                    objetivo_carga = self.energia.energia_max
                else:
                    destino = self.raton_mas_cercano(mapa)
                    if destino:
                        ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo   = dijkstra(mapa, destino, [self.deposito]) or []
                        ruta_base   = dijkstra(mapa, self.deposito, [self.base]) or []
                        costo_ciclo = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)
                        objetivo_carga = min(self.energia.energia_max, int(costo_ciclo * n_restantes * 1.2))
                    else:
                        objetivo_carga = self.energia.energia_max
            else:
                objetivo_carga = self.energia.energia_max
            
            if self.energia.valor < objetivo_carga:
                self.estado = "Descansando"
                self.recargando = True
                ahora = pygame.time.get_ticks()
                delta_ms = ahora - self.ultimo_tick
                recarga = (delta_ms / 1000) * self.energia.recarga_por_segundo
                self.energia.valor = min(objetivo_carga, self.energia.valor + recarga)
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
            if mapa[self.fila][self.col] == CELDA_RATON:
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

            destino = self.raton_mas_cercano(mapa)
            if destino:
                # rutas necesarias
                ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                ruta_depo   = dijkstra(mapa, destino, [self.deposito]) or []
                ruta_base   = dijkstra(mapa, self.deposito, [self.base]) or []

                costo_total = len(ruta_pelota) + len(ruta_depo) + len(ruta_base)

                if self.energia.valor >= int(costo_total * 1.1):
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
                    destino = self.raton_mas_cercano(mapa)
                    if destino:
                        ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo   = dijkstra(mapa, destino, [self.deposito]) or []
                        costo_hasta_depo = len(ruta_pelota) + len(ruta_depo)

                        if self.energia.valor >= int(costo_hasta_depo * 1.1):
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
        # energía depende del coste del terreno
            coste = COSTOS.get(mapa[nf][nc], 1)
            self.energia.valor = max(0, self.energia.valor - coste * self.energia.costo_paso)
# ---------------- Renderizado ----------------
    def dibujar(self, pantalla):
        dibujar(self, pantalla)
   
