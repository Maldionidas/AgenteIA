import pygame

# ================== Config ==================
SCALE = 12
PAD = 18
BG = (230, 230, 230)

# Paleta
T = (0,0,0,0)          # transparente
N = (0,0,0,255)        # contorno
B = (165,155,155,255)  # cuerpo
G = (120,110,110,255)  # sombra
P = (255,0,255,255)    # cachetes
CMAP = {' ':T,'N':N,'B':B,'G':G,'P':P}

# ============ FRONT ============
FRONT = [
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

# ============ BACK ============
BACK = [
    "     N     N          ",
    "    NBN   NBN         ",
    "    NBGNNNGBN         ",
    "   NGBBGGGBBGN        ",
    "   NBBBBBBBBBN        ",
    "  NGBBBBBBBBBGN       ",
    "  NBBBBBBBBBBBN       ",
    "  NBBBBBBBBBBBN       ",
    " NGBBBBBBBBBBBGN      ",
    " NGBBBBBBBBBBBGN      ",
    " NBBBBBBBBBBBBBN      ",
    " NBBBBBBBBBBBBBN      ",
    "NGGBBBBBBBBBBBGGN     ",
    "NGBBBBBBBBBBBBBGN     ",
    "NBBBBBBBBBBBBBBBN  NN ",
    "NGGBBBBBBBBBBBGGN NBBN",
    "NGBBBBBBBBBBBBBGN  NGN",
    "NBBBBBBBBBBBBBBBN  NBN",
    "NGBBBBBBBBBBBBBGNNNBBN",
    " NGBBBBBBBBBBBGBBBBBN ",
    "  NNNBNNNNNBNNNNNNNN  ",
    "    NNN   NNN         "
]

# ============ LEFT ============
LEFT = [
    "   N      N            ",
    "  NBN    NBN           ",
    "  NBGNNNNGBN        NN ",
    " NBBBGGBGBBGN      NBBN",
    " NBBBBBBBBBBN      NBBN",
    "NBBNBBNBBNBBGNNNN   NGN",
    "NBPBBNBNBBPBBGBGBN  NBN",
    "NBBBBBBBBBBBBGBGBBNNNGN",
    "NBBBBBBBBBBBBBBBBBBNBN ",
    "NBBBBBBBBBBBBBBBBBBNBN ",
    "NBBBBBBBBBBBBBBBBBBBN  ",
    "NGBBBBBBBBBBBBBBBBBBN  ",
    "NGBBBBBBBBBBBBBBBBBBN  ",
    "NGBBBBBBBBBBBBBBBBBGN  ",
    " NGBBBBBBBBBBBBBBBGN   ",
    "  NGBBBBGBBBGBGGBGN    ",
    "   NBNNBNNNNNBNNBN     ",
    "   NN  NN   NN  NN     "
]

# ---------------- Helpers ----------------
def check_rect(p):
    h=len(p); w=len(p[0])
    for i,row in enumerate(p):
        if len(row)!=w:
            raise ValueError(f"Fila {i} mide {len(row)}; debería medir {w}.")
        for ch in row:
            if ch not in CMAP:
                raise ValueError(f"Carácter inválido '{ch}' en fila {i}.")
    return w,h

def pixmap_to_surface(pat, scale=SCALE):
    w,h = check_rect(pat)
    surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)
    for y,row in enumerate(pat):
        for x,ch in enumerate(row):
            c = CMAP[ch]
            if c[3]==0: continue
            pygame.draw.rect(surf, c, (x*scale, y*scale, scale, scale))
    return surf

def mirror_h(pat):
    return [row[::-1] for row in pat]

# ---------------- Main ----------------
def main():
    pygame.init()
    font = pygame.font.SysFont(None, 22)

    surf_front = pixmap_to_surface(FRONT)
    surf_back  = pixmap_to_surface(BACK)             
    surf_left  = pixmap_to_surface(LEFT)
    surf_right = pixmap_to_surface(mirror_h(LEFT))   # espejo del lateral

    # Guardar
    pygame.image.save(surf_front, "cat_front.png")
    pygame.image.save(surf_back, "cat_back.png")
    pygame.image.save(surf_left, "cat_left.png")
    pygame.image.save(surf_right, "cat_right.png")

    # Ventana 2×2
    pad=PAD
    w1,h1 = surf_front.get_size()
    w2,h2 = surf_back.get_size()
    w3,h3 = surf_left.get_size()
    w4,h4 = surf_right.get_size()
    win = pygame.display.set_mode((max(w1,w3)+max(w2,w4)+3*pad, max(h1,h2)+max(h3,h4)+3*pad+24))
    pygame.display.set_caption("Front / Back / Left / Right")

    positions = {
        "Front": (pad, pad+24),
        "Back":  (pad + max(w1,w3) + pad, pad+24),
        "Left":  (pad, pad*2 + 24 + max(h1,h2)),
        "Right": (pad + max(w1,w3) + pad, pad*2 + 24 + max(h1,h2)),
    }

    running=True; clock=pygame.time.Clock()
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
        win.fill(BG)
        win.blit(font.render("Front",True,(40,40,40)), (positions["Front"][0], pad-2))
        win.blit(font.render("Back", True,(40,40,40)), (positions["Back"][0],  pad-2))
        win.blit(font.render("Left", True,(40,40,40)), (positions["Left"][0],  positions["Left"][1]-19))
        win.blit(font.render("Right",True,(40,40,40)), (positions["Right"][0], positions["Right"][1]-19))

        win.blit(surf_front, positions["Front"])
        win.blit(surf_back,  positions["Back"])
        win.blit(surf_left,  positions["Left"])
        win.blit(surf_right, positions["Right"])
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
