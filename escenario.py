import pygame, random
from config import *

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

        charco_png = pygame.image.load("personajes/charco.png").convert_alpha()
        charco_size = int(TAM * 0.9)
        self.charco_img = pygame.transform.smoothscale(charco_png, (charco_size, charco_size))

        plato_png = pygame.image.load("personajes/plato.png").convert_alpha()
        plato_size = int(TAM * 0.8)
        self.plato_img = pygame.transform.smoothscale(plato_png, (plato_size, plato_size))

        bola_png = pygame.image.load("personajes/bola.png").convert_alpha()
        bola_size = int(TAM * 0.8)
        self.bola_img = pygame.transform.smoothscale(bola_png, (bola_size, bola_size))

        self._deposito_imgs = self._cargar_sprites_deposito()

         # --- ÍTEMS TEMPORALES ---
        self.platos_pos = []
        self.bolas_pos = []
        self.plato_timer = 0
        self.bola_timer = 0

    def _cargar_sprites_deposito(self):
        """Carga y escala los 5 sprites del depósito (0..4+)."""
        nombres = [
            "personajes/deposito_0.png",
            "personajes/deposito_1.png",
            "personajes/deposito_2.png",
            "personajes/deposito_3.png",
            "personajes/deposito_4.png",  # 4 o más
        ]
        imgs = []
        size = int(TAM * 1.1)  
        for ruta in nombres:
            img = pygame.image.load(ruta).convert_alpha()
            imgs.append(pygame.transform.smoothscale(img, (size, size)))
        return imgs
    
    def _sprite_deposito_por_conteo(self, n):
        """Devuelve el sprite correcto según n ratones (4 == 4+)."""
        idx = 4 if n >= 4 else max(0, n)
        return self._deposito_imgs[idx]
    
    # ================== ÍTEMS TEMPORALES ==================
    def actualizar_items(self):
        """Controla aparición y reposicionamiento de plato y bola."""
        ahora = pygame.time.get_ticks()

        # Plato de leche cada 10s
        if ahora >= self.plato_timer:
            self.platos_pos = []
            for _ in range(4):  # ejemplo: 3 platos
                while True:
                    f = random.randint(1, FILAS-2)
                    c = random.randint(1, COLS-2)
                    if (f, c) not in [self.base, self.deposito] and self.mapa[f][c] == CELDA_VACIA:
                        self.platos_pos.append((f, c))
                        break
            self.plato_timer = ahora + 10000

        # cada 10s generamos varias bolas
        if ahora >= self.bola_timer:
            self.bolas_pos = []
            for _ in range(4):  # ejemplo: 4 bolas
                while True:
                    f = random.randint(1, FILAS-2)
                    c = random.randint(1, COLS-2)
                    if (f, c) not in [self.base, self.deposito] and self.mapa[f][c] == CELDA_VACIA:
                        self.bolas_pos.append((f, c))
                        break
            self.bola_timer = ahora + 10000



    def dibujar(self, pantalla):
        for fila in range(FILAS):
            for col in range(COLS):
                valor = self.mapa[fila][col]
                x = col * TAM
                y = fila * TAM

                if (fila, col) == self.base:
                    pygame.draw.rect(pantalla, BASE_COLOR, (x, y, TAM, TAM))
                    # Dibuja ratones contabilizados en BASE
                    #self._dibujar_stack(pantalla, x, y, self.entregados_base)

                elif (fila, col) == self.deposito:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    # Sprite del depósito según entregados_deposito
                    dep_img = self._sprite_deposito_por_conteo(self.entregados_deposito)
                    iw, ih = dep_img.get_size()
                    pantalla.blit(dep_img, (x + (TAM - iw)//2, y + (TAM - ih)//2))

                elif valor == CELDA_MURO:
                    pygame.draw.rect(pantalla, MURO, (x, y, TAM, TAM))

                elif valor == CELDA_RATON:
                    pygame.draw.rect(pantalla, CELDA_RATON, (x, y, TAM, TAM))
                    img_w, img_h = self.raton_img.get_size()
                    pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y + (TAM - img_h)//2))
                                    
                elif valor == CELDA_CHARCO:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))
                    iw, ih = self.charco_img.get_size()
                    pantalla.blit(self.charco_img, (x + (TAM - iw)//2, y + (TAM - ih)//2))


                else:
                    pygame.draw.rect(pantalla, VACIO, (x, y, TAM, TAM))

                pygame.draw.rect(pantalla, (100, 100, 100), (col*TAM, fila*TAM, TAM, TAM), 1)

        # === Dibujo de ítems temporales ===
        for f, c in self.platos_pos:
            x, y = c * TAM, f * TAM
            iw, ih = self.plato_img.get_size()
            pantalla.blit(self.plato_img, (x + (TAM - iw)//2, y + (TAM - ih)//2))

        for f, c in self.bolas_pos:
            x, y = c * TAM, f * TAM
            iw, ih = self.bola_img.get_size()
            pantalla.blit(self.bola_img, (x + (TAM - iw)//2, y + (TAM - ih)//2))


    def _dibujar_stack(self, pantalla, x, y, n):
        """Dibuja n ratones en una retícula 2x2 (hasta 4)."""
        if n <= 0:
            return

        img_w, img_h = self.raton_img.get_size()

        # ligerito a la derecha y abajo
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
