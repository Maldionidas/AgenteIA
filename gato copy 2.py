import pygame

# =============== Config ===============
SCALE = 12                 # tamaño de cada "pixel" en pantalla
OUT_PNG = "gatito_front.png"

# Paleta (RGBA) SEGÚN TUS LETRAS:
T = (0, 0, 0, 0)              # ' '  transparente
N = (0, 0, 0, 255)            # 'N'  negro (contorno)
B = (165, 155, 155, 255)      # 'B'  gris claro del cuerpo
G = (120, 110, 110, 255)      # 'G'  gris oscuro (sombras)
P = (255, 0, 255, 255)        # 'P'  magenta (cachetes)

# =============== Sprite (23 x 18) ===============
SPRITE_16 = [
    "     N     N          ",
    "    NBN   NBN         ",
    "    NBGNNNGBN         ", 
    "   NGBBGGGBBGN        ",
    "   NBBBBBBBBBN        ",
    "  NGBBBBBBBBBGN       ",
    "  NBBNBBNBBNBBN       ",
    "  NBPBBNBNBBPBN       ",
    " NGBBBBBBBBBBBGN      ",
    " NGBBBBBBBBBBBGN      ",
    " NBBBBBBBBBBBBBN      ",
    " NBBBBBBBBBBBBBN      ",
    "NGGBBBBBBBBBBBGGN     ",
    "NGBBBBBBBBBBBBBGN     ",
    "NBBBBBBBBBBBBBBBN  NN ",
    "NGGBBBBBBBBBBBGGN NBBN",
    "NGBBBBBBBBBBBBBGN  NGN",
    "NBBBNBBBBBBBNBBBN  NBN",
    "NGBBNBNBBBNBNBBGNNNBBN",
    " NGBNBNBBBNBNBGBBBBBN ",
    "  NNNBNNNNNBNNNNNNNN  ",
    "    NNN   NNN         " 
]

def pixmap_to_surface(pattern, scale):
    # mapa de caracteres -> color, AHORA con tus claves
    cmap = {' ': T, 'N': N, 'B': B, 'G': G, 'P': P}

    h = len(pattern)
    w = len(pattern[0])
    # (opcional) validar rectangular
    for i, row in enumerate(pattern):
        if len(row) != w:
            raise ValueError(f"Fila {i} mide {len(row)}; debería medir {w}.")

    surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            color = cmap.get(ch, T)   # cualquier letra no listada = transparente
            if color[3] == 0:
                continue
            pygame.draw.rect(surf, color, (x*scale, y*scale, scale, scale))
    return surf

def main():
    pygame.init()
    sprite = pixmap_to_surface(SPRITE_16, SCALE)

    win = pygame.display.set_mode((sprite.get_width(), sprite.get_height()))
    pygame.display.set_caption("Gatito pixel – vista frontal")

    pygame.image.save(sprite, OUT_PNG)
    print(f"Guardado: {OUT_PNG}")

    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        win.fill((220, 220, 220))
        win.blit(sprite, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
