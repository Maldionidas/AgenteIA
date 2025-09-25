import pygame
from .energia import Energia
from config import TAM, COLS


 # --------------- Render ---------------
def dibujar(self, pantalla):
        x = self.col * TAM
        y = self.fila * TAM
        pantalla.blit(self.images[self.dir], (x, y))
        # --- Gato animaciones ---
        if self.animando:
            img_w, img_h = self.raton_img.get_size()
            pantalla.blit(self.raton_img, (x + (TAM - img_w)//2, y - img_h//2))

        if self.cargando:
            img_w, img_h = self.raton_img.get_size()
            offset_x = (TAM - img_w) // 2
            offset_y = (TAM - img_h) // 2 - 6
            pantalla.blit(self.raton_img, (x + offset_x, y + offset_y))
        # --- Deposito de los ratones ---
        dx = self.deposito[1] * TAM
        dy = self.deposito[0] * TAM
        label = self.font.render(str(self.contador_deposito), True, (255, 255, 255))
        bg = label.get_rect()
        bg.topright = (dx + TAM - 3, dy + 3)
        bg.inflate_ip(6, 2)
        pygame.draw.rect(pantalla, (0, 0, 0), bg)
        pantalla.blit(label, (bg.right - label.get_width() - 3, bg.top + 1))


        ##  --- Barra de energía ---
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