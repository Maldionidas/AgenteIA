import pygame
import math
from config import TAM, COLS, FILAS
from .constants import PATH_RGBA

def _ruta_posiciones_desde_acciones(start_rc, acciones):
    # Convierte ["arriba","derecha",...] a lista de (f,c) visitadas
    f, c = start_rc
    out = []
    for a in acciones or []:
        if a == "arriba":    f -= 1
        elif a == "abajo":   f += 1
        elif a == "izquierda": c -= 1
        elif a == "derecha":   c += 1
        out.append((f, c))
    return out

def dibujar(self, pantalla):
    x = self.col * TAM
    y = self.fila * TAM
    pantalla.blit(self.images[self.dir], (x, y))

    # --- Dibujar la ruta planeada (vista previa) ---
    if getattr(self, "ruta", None):
        path_surf = pygame.Surface((TAM, TAM), pygame.SRCALPHA)
        path_surf.fill(PATH_RGBA)
        # calculamos pos futuras desde (fila,col) y acciones pendientes
        posiciones = _ruta_posiciones_desde_acciones((self.fila, self.col), self.ruta)
        for (rf, rc) in posiciones:
            if 0 <= rf < FILAS and 0 <= rc < COLS:
                pantalla.blit(path_surf, (rc * TAM, rf * TAM))

    # --- Animación de recoger (ratón sobre la cabeza) ---
    if getattr(self, "animando", False):
        img_w, img_h = self.raton_img.get_size()
        pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y - img_h//2))

    # --- Indicador de que carga un ratón (sobre el cuerpo) ---
    if getattr(self, "cargando", False):
        img_w, img_h = self.raton_img.get_size()
        offset_x = (TAM - img_w) // 2
        offset_y = (TAM - img_h) // 2 - 6
        pantalla.blit(self.raton_img, (x + offset_x, y + offset_y))

    # --- Animación "Jugando con la pelota" ---
    if getattr(self, "jugando", False):
        if not hasattr(self, "_bola_img_raw"):
            bola = pygame.image.load("personajes/bola.png").convert_alpha()
            size = int(TAM * 0.45)
            self._bola_img_raw = pygame.transform.scale(bola, (size, size))
        t = pygame.time.get_ticks() / 1000.0
        angle = (t * 180) % 360
        bola_rot = pygame.transform.rotate(self._bola_img_raw, angle)
        bw, bh = bola_rot.get_size()
        r = int(TAM * 0.30)
        ox = int(r * math.cos(t * 4.0))
        oy = int(r * math.sin(t * 4.0)) - int(TAM * 0.10)
        cx = x + TAM // 2 + ox - bw // 2
        cy = y + TAM // 2 + oy - bh // 2
        pantalla.blit(bola_rot, (cx, cy))

    # --- Barra de energía / HUD y estado (como lo tenías) ---
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
    pct = 0 if self.energia.energia_max == 0 else self.energia.valor / self.energia.energia_max
    pygame.draw.rect(pantalla, (50, 200, 50), (hud_x, hud_y, int(bar_w * pct), bar_h))
    txt = self.font.render("ENERGIA", True, (255, 255, 255))
    pantalla.blit(txt, (hud_x, hud_y + bar_h + 4))

    estado_txt = self.font.render(f"Estado: {self.estado}", True, (255, 255, 255))
    fondo = estado_txt.get_rect()
    fondo.midtop = (COLS * TAM // 2, 5)
    pygame.draw.rect(pantalla, (0, 0, 0), fondo.inflate(10, 6))
    pantalla.blit(estado_txt, estado_txt.get_rect(center=fondo.center))
