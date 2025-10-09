# AgenteIA.py
import pygame
from config import (
    TAM, FILAS, COLS,
    CELDA_MURO, CELDA_RATON, CELDA_VACIA,
    CELDA_COMIDA, CELDA_ESTAMBRE,  # ← necesarios para plato y estambre
    COSTOS
)

VISION_CELDAS = 7

from .busquedaRuta import dijkstra
from .energia import Energia
from .animaciones import Animaciones
from .render import dibujar


class AgenteIA:
    def __init__(self, fila, col, base, deposito, color=(200, 50, 50)):
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

        # --- Animación de recoger ---
        self.animando = False
        self.inicio_animacion = 0
        self.tiempo_animacion = 1000  # 1 segundo en ms
        self.estado = "Idle"  # leyenda de estado

        self.font = pygame.font.SysFont(None, max(16, int(TAM * 0.6)))
        self.base = base
        self.deposito = deposito

        # Energía
        self.energia = Energia(energia_max=300, recarga_por_segundo=40, costo_paso=1)

        # Sprites del gato
        self.images = {
            "front": pygame.image.load("personajes/cat_front.png").convert_alpha(),
            "back": pygame.image.load("personajes/cat_back.png").convert_alpha(),
            "left": pygame.image.load("personajes/cat_left.png").convert_alpha(),
            "right": pygame.image.load("personajes/cat_right.png").convert_alpha(),
        }
        for k, img in self.images.items():
            self.images[k] = pygame.transform.scale(img, (TAM, TAM))
        self.dir = "front"

        # Sprite del ratón
        self.raton_img = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(self.raton_img, (raton_size, raton_size))

        # Re-enfoque periódico (ya lo teníamos)
        self._ultimo_recalculo = 0
        self._cooldown_recalculo_ms = 300

        # Para la recarga en base
        self.recargando = False
        self.ultimo_tick = pygame.time.get_ticks()
        self.persiguiendo = False  # True solo cuando hay un ratón dentro de visión y lo estamos cazando

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

    def raton_visible_mas_cercano(self, mapa):
        """
        Devuelve (pos_raton, ruta_acciones) si hay un ratón alcanzable
        en <= VISION_CELDAS pasos. Si no, (None, []).
        """
        ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
        mejor = None
        mejor_ruta = None
        for p in ratones:
            r = dijkstra(mapa, (self.fila, self.col), [p]) or []
            if r and len(r) <= VISION_CELDAS:
                if mejor_ruta is None or len(r) < len(mejor_ruta):
                    mejor = p
                    mejor_ruta = r
        return (mejor, (mejor_ruta or []))

    def _recalcular_si_conviene(self, mapa):
        if self.cargando or self.animando or self.fue_deposito:
            return
        if not self.ruta:
            return

        ahora = pygame.time.get_ticks()
        if ahora - self._ultimo_recalculo < self._cooldown_recalculo_ms:
            return
        self._ultimo_recalculo = ahora

        # Si el objetivo dejó de ser un ratón válido, buscar otro pero SOLO si está en visión
        if self.objetivo is None or self.objetivo[0] < 0 or self.objetivo[1] < 0:
            destino, ruta_vis = self.raton_visible_mas_cercano(mapa)
            if destino:
                self._ruta_hacia(mapa, destino)
                self.persiguiendo = True
                self.estado = "Persiguiendo (re-enfoque)"
            else:
                # nada a la vista: salimos del modo persecución
                self.persiguiendo = False
            return

        of, oc = self.objetivo
        if not (0 <= of < FILAS and 0 <= oc < COLS) or mapa[of][oc] != CELDA_RATON:
            destino, ruta_vis = self.raton_visible_mas_cercano(mapa)
            if destino:
                self._ruta_hacia(mapa, destino)
                self.persiguiendo = True
                self.estado = "Persiguiendo (re-enfoque)"
            else:
                self.persiguiendo = False
            return

        # Comparar longitudes de ruta pero solo con un ratón VISIBLE
        ruta_restante_len = len(self.ruta)
        destino_cercano, ruta_cercana = self.raton_visible_mas_cercano(mapa)
        if not destino_cercano or not ruta_cercana:
            # si ya no hay visibles, sal de persecución
            self.persiguiendo = False
            return

        if destino_cercano == self.objetivo:
            return

        if len(ruta_cercana) < ruta_restante_len:
            self._ruta_hacia(mapa, destino_cercano)
            self.persiguiendo = True
            self.estado = "Re-enfocando al ratón visible más cercano"

    # --------------- Lógica principal ---------------
    def actualizar(self, mapa):
        # --- Parámetros locales (no tocan otros archivos) ---
        VISION = 7  # pasos máximos para "ver" algo (respeta muros con dijkstra)
        COSTO_SPRINT = 1.5  # energía/step cuando persigue
        COSTO_NORMAL = 1.0  # energía/step normal
        JUEGO_MS = 2000  # 2s jugando con estambre
        BEBER_MS = 3000  # 3s bebiendo leche
        DRENA_JUEGO_POR_SEG = 0.4  # drenaje suave mientras juega (energía/seg)

        # --- Flags/Timers que quizá no existan aún (asegurar) ---
        if not hasattr(self, "persiguiendo"):
            self.persiguiendo = False
        if not hasattr(self, "jugando"):
            self.jugando = False
            self.inicio_juego = 0
            self.tiempo_juego_ms = JUEGO_MS
            self._ultimo_tick_juego = pygame.time.get_ticks()
        if not hasattr(self, "bebiendo"):
            self.bebiendo = False
            self.inicio_bebida = 0
            self.tiempo_bebida_ms = BEBER_MS
        # --- NUEVO: flags anti-retrigger mínimos ---
        if not hasattr(self, "_evitar_retrigger_estambre"):
            self._evitar_retrigger_estambre = False
        if not hasattr(self, "_evitar_retrigger_leche"):
            self._evitar_retrigger_leche = False

        # costo por paso según si persigue
        self.energia.costo_paso = COSTO_SPRINT if self.persiguiendo else COSTO_NORMAL

        # helpers: objetivos visibles por tipo de celda
        def objetivo_visible_por_celda(celda_obj):
            candidatos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == celda_obj]
            mejor = None
            mejor_ruta = None
            for p in candidatos:
                r = dijkstra(mapa, (self.fila, self.col), [p]) or []
                if r and len(r) <= VISION:
                    if mejor_ruta is None or len(r) < len(mejor_ruta):
                        mejor, mejor_ruta = p, r
            return mejor, mejor_ruta

        def raton_visible_y_ruta():
            candidatos = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
            mejor = None
            mejor_ruta = None
            for p in candidatos:
                r = dijkstra(mapa, (self.fila, self.col), [p]) or []
                if r and len(r) <= VISION:
                    if mejor_ruta is None or len(r) < len(mejor_ruta):
                        mejor, mejor_ruta = p, r
            return mejor, mejor_ruta

        # --- Estado: BEBIENDO (tiene prioridad, ignora energía baja durante 3s) ---
        if self.bebiendo:
            self.estado = "Bebiendo leche"
            if pygame.time.get_ticks() - self.inicio_bebida >= self.tiempo_bebida_ms:
                self.bebiendo = False
                self.energia.valor = self.energia.energia_max
                self.estado = "Energía recuperada"
            return

        # --- Estado: JUGANDO con estambre (si se queda sin energía, cancela y va a base) ---
        if self.jugando:
            ahora = pygame.time.get_ticks()
            delta = (ahora - getattr(self, "_ultimo_tick_juego", ahora)) / 1000.0
            self._ultimo_tick_juego = ahora
            if self.energia.valor > 0:
                self.energia.valor = max(0, self.energia.valor - DRENA_JUEGO_POR_SEG * delta)

            self.estado = "Jugando con estambre"
            if ahora - self.inicio_juego >= self.tiempo_juego_ms:
                self.jugando = False
                self.estado = "Listo"
            elif self.energia.valor <= 0 and (self.fila, self.col) != self.base:
                self.jugando = False
                self.persiguiendo = False
                self.estado = "Sin energía, regresando a base"
                self._ruta_hacia(mapa, self.base)
            return

        # --- Sin energía fuera de base: cancelar todo y volver a base ---
        if self.energia.valor <= 0 and (self.fila, self.col) != self.base:
            self.persiguiendo = False
            self.estado = "Sin energía, regresando a base"
            if self.objetivo != self.base or not self.ruta:
                self._ruta_hacia(mapa, self.base)
            if self.ruta:
                accion = self.ruta.pop(0)
                self.mover(accion, mapa)
            return

        # --- Animación de recoger ratón (igual) ---
        if self.animando:
            self.estado = "Recogiendo ratón"
            ahora = pygame.time.get_ticks()
            if ahora - self.inicio_animacion >= self.tiempo_animacion:
                self.animando = False
                self.cargando = True
                mapa[self.fila][self.col] = CELDA_VACIA
                self.estado = "Yendo a depositar ratón"
                self.persiguiendo = False
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)
            return

        # --- En base: recarga como ya lo tenías ---
        if (self.fila, self.col) == self.base:
            self.persiguiendo = False
            ratones = [(f, c) for f in range(FILAS) for c in range(COLS) if mapa[f][c] == CELDA_RATON]
            n_restantes = len(ratones)

            if n_restantes > 0:
                if n_restantes >= 4:
                    objetivo_carga = self.energia.energia_max
                else:
                    destino = self.raton_mas_cercano(mapa)
                    if destino:
                        ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                        ruta_depo = dijkstra(mapa, destino, [self.deposito]) or []
                        ruta_base = dijkstra(mapa, self.deposito, [self.base]) or []
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

        # --- Al pisar un ratón: iniciar animación ---
        if not self.cargando and not self.fue_deposito:
            if mapa[self.fila][self.col] == CELDA_RATON:
                self.animando = True
                self.inicio_animacion = pygame.time.get_ticks()
                self.estado = "Recogiendo ratón"
                self.objetivo = None
                self.ruta = []
                self.persiguiendo = False
                mapa[self.fila][self.col] = CELDA_VACIA
                return

        # --- NUEVO: Al pisar PLATO (beber 3s y restaurar energía) ---
        if mapa[self.fila][self.col] == CELDA_COMIDA and not self._evitar_retrigger_leche:
            self.estado = "Bebiendo leche"
            self.bebiendo = True
            self.inicio_bebida = pygame.time.get_ticks()
            self.objetivo = None
            self.ruta = []
            self.persiguiendo = False
            self._evitar_retrigger_leche = True  # evita re-disparo mientras está quieto en la misma celda
            mapa[self.fila][self.col] = CELDA_VACIA  # consumir plato
            return

        # --- NUEVO: Al pisar ESTAMBRE (jugar 2s, gasta un poco, cancela persecución) ---
        if mapa[self.fila][self.col] == CELDA_ESTAMBRE and not self._evitar_retrigger_estambre:
            self.estado = "Jugando con estambre"
            self.jugando = True
            self.inicio_juego = pygame.time.get_ticks()
            self._ultimo_tick_juego = self.inicio_juego
            self.objetivo = None
            self.ruta = []
            self.persiguiendo = False
            self._evitar_retrigger_estambre = True  # evita re-disparo hasta moverse
            return

        # --- Al llegar al depósito con un ratón (igual) ---
        if self.cargando and (self.fila, self.col) == self.deposito:
            self.cargando = False
            self.contador_deposito += 1
            self.objetivo = None
            self.ruta = []
            self.persiguiendo = False

            destino = self.raton_mas_cercano(mapa)
            if destino:
                ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                ruta_depo = dijkstra(mapa, destino, [self.deposito]) or []
                ruta_base = dijkstra(mapa, self.deposito, [self.base]) or []
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

        # --- PRIORIDAD DURA: si ve PLATO, va de inmediato (interrumpe lo que sea) ---
        plato_obj, plato_ruta = objetivo_visible_por_celda(CELDA_COMIDA)
        if plato_obj and plato_ruta and plato_obj != (self.fila, self.col) and not self.bebiendo:
            self.estado = "A por leche"
            self.persiguiendo = False
            self._ruta_hacia(mapa, plato_obj)

        # --- Planear ruta si no hay pendiente ---
        if not self.ruta:
            if self.cargando:
                self.estado = "Yendo a depositar ratón"
                if self.deposito:
                    self._ruta_hacia(mapa, self.deposito)
            else:
                if self.fue_deposito:
                    self.estado = "Descansando"
                    self.persiguiendo = False
                    self._ruta_hacia(mapa, self.base)
                else:
                    # 1) ¿Hay estambre visible? => ir a jugar (cancela persecución)
                    est_obj, est_ruta = objetivo_visible_por_celda(CELDA_ESTAMBRE)
                    if est_obj and est_ruta and est_obj != (self.fila, self.col):
                        self.estado = "Yendo a jugar"
                        self.persiguiendo = False
                        self._ruta_hacia(mapa, est_obj)
                    else:
                        # 2) ¿Hay ratón visible? => PERSEGUIR (gasta 1.5/step)
                        vis_obj, vis_ruta = raton_visible_y_ruta()
                        if vis_obj and vis_ruta:
                            self.estado = "Persiguiendo"
                            self.persiguiendo = True
                            self.energia.costo_paso = COSTO_SPRINT
                            self._ruta_hacia(mapa, vis_obj)
                        else:
                            # 3) Comportamiento previo: ir al más cercano si alcanza energía
                            destino = self.raton_mas_cercano(mapa)
                            if destino:
                                ruta_pelota = dijkstra(mapa, (self.fila, self.col), [destino]) or []
                                ruta_depo = dijkstra(mapa, destino, [self.deposito]) or []
                                costo_hasta_depo = len(ruta_pelota) + len(ruta_depo)

                                if self.energia.valor >= int(costo_hasta_depo * 1.1):
                                    self.estado = "Buscando ratón"
                                    self.persiguiendo = False
                                    self.energia.costo_paso = COSTO_NORMAL
                                    self._ruta_hacia(mapa, destino)
                                else:
                                    self.estado = "Cansancio al límite"
                                    self.persiguiendo = False
                                    self.energia.costo_paso = COSTO_NORMAL
                                    self._ruta_hacia(mapa, self.base)
                            else:
                                self.objetivo = None
                                self.persiguiendo = False
                                self.energia.costo_paso = COSTO_NORMAL

        # --- Salvaguarda de energía (igual) ---
        if not self.cargando and (self.fila, self.col) != self.base and not self.bebiendo and not self.jugando:
            ruta_base_tmp = dijkstra(mapa, (self.fila, self.col), [self.base]) or []
            costo_base = len(ruta_base_tmp) if ruta_base_tmp else 10 ** 9
            if self.energia.valor <= (int(costo_base * 1.05) + 1):
                if self.objetivo != self.base:
                    self.estado = "Regresando a base (ahorro energía)"
                    self.persiguiendo = False
                    self.energia.costo_paso = COSTO_NORMAL
                    self._ruta_hacia(mapa, self.base)

        # --- Re-enfoque solo si NO está persiguiendo (evita temblor de objetivos) ---
        if not self.persiguiendo and not self.bebiendo and not self.jugando:
            self._recalcular_si_conviene(mapa)
        else:
            # Si persigue pero perdió objetivo visible, volver a flujo normal
            if self.persiguiendo:
                of, oc = self.objetivo or (-1, -1)
                if self.objetivo is None or not (0 <= of < FILAS and 0 <= oc < COLS) or mapa[of][oc] != CELDA_RATON:
                    vis_obj, vis_ruta = raton_visible_y_ruta()
                    if vis_obj and vis_ruta:
                        self._ruta_hacia(mapa, vis_obj)
                        self.estado = "Persiguiendo"
                    else:
                        self.persiguiendo = False
                        self.energia.costo_paso = COSTO_NORMAL
                        self.estado = "Buscando ratón"
                        destino = self.raton_mas_cercano(mapa)
                        if destino:
                            self._ruta_hacia(mapa, destino)

        # --- Paso final de movimiento ---
        if self.ruta and not self.bebiendo and not self.jugando:
            accion = self.ruta.pop(0)
            self.mover(accion, mapa)

    # --------------- Movimiento ---------------
    def mover(self, accion, mapa):
        df, dc = 0, 0
        if accion == "arriba":
            df = -1;
            self.dir = "back"
        elif accion == "abajo":
            df = 1;
            self.dir = "front"
        elif accion == "izquierda":
            dc = -1;
            self.dir = "left"
        elif accion == "derecha":
            dc = 1;
            self.dir = "right"

        nf = self.fila + df
        nc = self.col + dc
        if 0 <= nf < FILAS and 0 <= nc < COLS and mapa[nf][nc] != CELDA_MURO:
            self.fila, self.col = nf, nc
            # energía depende del coste del terreno
            coste = COSTOS.get(mapa[nf][nc], 1)
            # Si estamos en 0, mantener en 0 para que pueda "arrastrarse" a la base
            if self.energia.valor > 0:
                self.energia.valor = max(0, self.energia.valor - coste * self.energia.costo_paso)

            # --- NUEVO: resetear flags anti-retrigger al moverse ---
            self._evitar_retrigger_estambre = False
            self._evitar_retrigger_leche = False

    # ---------------- Renderizado ----------------
    def dibujar(self, pantalla):
        dibujar(self, pantalla)
