# escenario.py
import pygame
import random
from config import *
from raton import Raton

# --- Clase Escenario ---
class Escenario:
    def __init__(self, mapa, base, deposito):
        self.mapa = mapa
        self.base = base
        self.deposito = deposito

        # contadores visibles independientes
        self.entregados_base = 0
        self.entregados_deposito = 0

        original = pygame.image.load("personajes/raton.png").convert_alpha()
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(original, (raton_size, raton_size))

        # --- NUEVO: instancias de ratones móviles, leemos del mapa inicial ---
        self.ratones = []
        for f in range(FILAS):
            for c in range(COLS):
                if self.mapa[f][c] == CELDA_RATON:
                    self.ratones.append(Raton(f, c, tick_ms=400))
        # (el valor CELDA_RATON seguirá en mapa; nos sincronizamos cada frame)

    def _sincronizar_lista_con_mapa(self):
        """
        Si el gato levantó un ratón (la celda dejó de ser CELDA_RATON),
        eliminamos ese ratón de la lista.
        """
        vivos = []
        for r in self.ratones:
            if 0 <= r.fila < FILAS and 0 <= r.col < COLS and self.mapa[r.fila][r.col] == CELDA_RATON:
                vivos.append(r)
        self.ratones = vivos

    def _actualizar_ratones(self):
        """
        Mover ratones y actualizar el mapa.
        Estrategia:
          1) Primero liberamos TODAS las celdas de ratón -> VACÍA (para no bloquearse entre sí).
          2) Actualizamos cada ratón (elige destino en VACÍAS).
          3) Re-escribimos CELDA_RATON en las posiciones finales de los ratones, evitando colisiones.
        """
        # Paso 1: liberar
        for r in self.ratones:
            if self.mapa[r.fila][r.col] == CELDA_RATON:
                self.mapa[r.fila][r.col] = CELDA_VACIA

        # Paso 2: mover en orden aleatorio para evitar sesgo
        orden = list(self.ratones)
        random.shuffle(orden)
        ocupadas = set()
        for r in orden:
            pos_antes = (r.fila, r.col)
            r.actualizar(self.mapa)  # intenta moverse a una celda VACÍA
            pos_despues = (r.fila, r.col)

            # Evitar que 2 ratones terminen en la misma celda:
            if pos_despues in ocupadas:
                # revertimos si colisionaría
                r.fila, r.col = pos_antes
                pos_despues = pos_antes

            ocupadas.add(pos_despues)

        # Paso 3: re-colocar bandera CELDA_RATON donde quedaron
        for r in self.ratones:
            # Ojo: si el gato justo está encima y la celda ya no es ratón, se respeta el cambio del gato.
            if self.mapa[r.fila][r.col] == CELDA_VACIA:
                self.mapa[r.fila][r.col] = CELDA_RATON

    def dibujar(self, pantalla):
        # --- NUEVO: antes de dibujar, sincronizamos y movemos ratones ---
        self._sincronizar_lista_con_mapa()
        self._actualizar_ratones()

        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                #base y depósito
                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, BASE_COLOR, (x, y, TAM, TAM))
                    #self._dibujar_stack(pantalla, x, y, self.entregados_base)

                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, DEPOSITO_COLOR, (x, y, TAM, TAM))
                    self._dibujar_stack(pantalla, x, y, self.entregados_deposito)

                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))
                
                #ratones
                elif valor == CELDA_RATON:
                    pygame.draw.rect(pantalla, CELDA_RATON, (x, y, TAM, TAM))
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))
                    
                # Agua
                elif valor == CELDA_AGUA:
                    pygame.draw.rect(pantalla, (0, 150, 255), (x, y, TAM, TAM))

                # Alfombra
                elif valor == CELDA_ALFOMBRA:
                    pygame.draw.rect(pantalla, (255, 200, 150), (x, y, TAM, TAM))

                # Celdas vacías
                elif valor == CELDA_VACIA:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

    def _dibujar_stack(self, pantalla, x, y, n):
        """Dibuja n ratones en una retícula 2x2 (hasta 4)."""
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
