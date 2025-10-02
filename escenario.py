import pygame
import random
from config import *
from raton import Raton

# ---- Rutas de texturas (ajusta si tus imágenes están en otra carpeta/nombre) ----
TEXTURAS_PATHS = {
    "cama": "personajes/cama.png",
    "deposito_0": "personajes/deposito_0.png",
    "deposito_1": "personajes/deposito_1.png",
    "deposito_2": "personajes/deposito_2.png",
    "deposito_3": "personajes/deposito_3.png",
    "deposito_4": "personajes/deposito_4.png",
    "charco": "personajes/charco.png",
    "bola": "personajes/bola.png",
    "plato": "personajes/plato.png",
}

def _cargar_img(ruta, tam=TAM):
    img = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.scale(img, (tam, tam))

# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base, deposito):
        self.mapa = mapa
        self.base = base
        self.deposito = deposito

        # contadores visibles independientes
        self.entregados_base = 0
        self.entregados_deposito = 0

        # Imagen del ratón (ya la tenías)
        original = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(original, (raton_size, raton_size))

        # --- NUEVO: texturas ---
        self.img_cama = _cargar_img(TEXTURAS_PATHS["cama"])
        self.img_charco = _cargar_img(TEXTURAS_PATHS["charco"])
        self.img_estambre = _cargar_img(TEXTURAS_PATHS["bola"])
        self.img_plato = _cargar_img(TEXTURAS_PATHS["plato"])
        self.img_cajas = [
            _cargar_img(TEXTURAS_PATHS["deposito_0"]),
            _cargar_img(TEXTURAS_PATHS["deposito_1"]),
            _cargar_img(TEXTURAS_PATHS["deposito_2"]),
            _cargar_img(TEXTURAS_PATHS["deposito_3"]),
            _cargar_img(TEXTURAS_PATHS["deposito_4"]),
        ]

        # --- NUEVO: instancias de ratones móviles, leemos del mapa inicial ---
        self.ratones = []
        for f in range(FILAS):
            for c in range(COLS):
                if self.mapa[f][c] == CELDA_RATON:
                    self.ratones.append(Raton(f, c, tick_ms=400))

        # --- NUEVO: platos de comida spawn cada 2 min ---
        self.food_interval_ms = 120_000  # 2 minutos
        self._last_food_spawn = pygame.time.get_ticks()
        self._platos_colocados = 0  # opcional: contador si te sirve

    def _sincronizar_lista_con_mapa(self):
        """Si el gato levantó un ratón (la celda dejó de ser CELDA_RATON), lo eliminamos de la lista."""
        vivos = []
        for r in self.ratones:
            if 0 <= r.fila < FILAS and 0 <= r.col < COLS and self.mapa[r.fila][r.col] == CELDA_RATON:
                vivos.append(r)
        self.ratones = vivos

    def _actualizar_ratones(self):
        """
        Mover ratones y actualizar el mapa.
        1) Liberamos celdas ratón -> VACÍA
        2) Movemos en orden aleatorio solo a VACÍAS (evitan agua/alfombra/base/depósito por definición)
        3) Recolocamos CELDA_RATON; evitamos colisiones
        """
        # Paso 1: liberar
        for r in self.ratones:
            if self.mapa[r.fila][r.col] == CELDA_RATON:
                self.mapa[r.fila][r.col] = CELDA_VACIA

        # Paso 2: mover
        orden = list(self.ratones)
        random.shuffle(orden)
        ocupadas = set()
        for r in orden:
            pos_antes = (r.fila, r.col)
            r.actualizar(self.mapa)
            pos_despues = (r.fila, r.col)
            if pos_despues in ocupadas:
                r.fila, r.col = pos_antes
                pos_despues = pos_antes
            ocupadas.add(pos_despues)

        # Paso 3: re-colocar bandera
        for r in self.ratones:
            if self.mapa[r.fila][r.col] == CELDA_VACIA:
                self.mapa[r.fila][r.col] = CELDA_RATON

    # ---- Spawn de platos de comida cada 2 minutos (no agua, no alfombra, no base/depósito, no encerrado) ----
    def _spawn_plato_si_toca(self):
        ahora = pygame.time.get_ticks()
        if ahora - self._last_food_spawn < self.food_interval_ms:
            return
        self._last_food_spawn = ahora
        # Elegir celda válida
        candidatos = [(f, c) for f in range(FILAS) for c in range(COLS)
                      if self.mapa[f][c] == CELDA_VACIA and (f, c) not in (self.base, self.deposito)]
        random.shuffle(candidatos)
        for f, c in candidatos:
            # No alfombra, no agua (ya garantizado por == VACIA)
            # No encerrado por muros: al menos un vecino no muro
            vecinos = [ (f-1,c), (f+1,c), (f,c-1), (f,c+1) ]
            accesible = False
            for nf, nc in vecinos:
                if 0 <= nf < FILAS and 0 <= nc < COLS and self.mapa[nf][nc] != CELDA_MURO:
                    accesible = True
                    break
            if not accesible:
                continue
            # Colocar plato
            self.mapa[f][c] = CELDA_COMIDA
            self._platos_colocados += 1
            break

    def dibujar(self, pantalla):
        # Actualizaciones antes del render
        self._sincronizar_lista_con_mapa()
        self._actualizar_ratones()
        self._spawn_plato_si_toca()

        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                # --- Base (cama) ---
                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_cama, (x, y))

                # --- Depósito (caja con 0..4 ratones visibles) ---
                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    idx = self.entregados_deposito
                    if idx > 4:
                        idx = 4
                    pantalla.blit(self.img_cajas[idx], (x, y))

                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))
                
                # --- Ratones sueltos ---
                elif valor == CELDA_RATON:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))
                    
                # --- Agua (charco con textura) ---
                elif valor == CELDA_AGUA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_charco, (x, y))

                # --- Alfombra ---
                elif valor == CELDA_ALFOMBRA:
                    pygame.draw.rect(pantalla, (255, 200, 150), (x, y, TAM, TAM))

                # --- Estambre (textura) ---
                elif valor == CELDA_ESTAMBRE:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_estambre, (x, y))

                # --- Comida (plato, aparece 1 cada 2 minutos) ---
                elif valor == CELDA_COMIDA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    pantalla.blit(self.img_plato, (x, y))

                # --- Celdas vacías ---
                elif valor == CELDA_VACIA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                # Grid
                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

    def _dibujar_stack(self, pantalla, x, y, n):
        """(Se deja por si lo quieres usar; ahora la caja ya muestra 0..4 visualmente)"""
        if n <= 0:
            return
        img_w, img_h = self.raton_img.get_size()
        dx = 2
        dy = 5
        offsets = [
            (TAM*0.15 + dx, TAM*0.15 + dy),  # arriba-izq
            (TAM*0.55 + dx, TAM*0.15 + dy),  # arriba-der
            (TAM*0.15 + dx, TAM*0.55 + dy),  # abajo-izq
            (TAM*0.55 + dx, TAM*0.55 + dy),  # abajo-der
        ]
        for i in range(min(n, 4)):
            ox, oy = offsets[i]
            pantalla.blit(self.raton_img, (x + ox - img_w/2, y + oy - img_h/2))
