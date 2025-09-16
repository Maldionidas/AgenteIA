import pygame

# =============== Config ===============
SCALE = 12   # tamaño de cada "pixel" en pantalla (sube/baja a gusto)
OUT_PNG = "gatito_front.png"

# Paleta (RGBA): colores exactos de la imagen
T = (0, 0, 0, 0)              # transparente
K = (0, 0, 0, 255)            # negro (contorno)
G = (165, 155, 155, 255)      # gris claro del cuerpo 
D = (120, 110, 110, 255)      # gris oscuro para sombras
P = (255, 0, 255, 255)        # magenta brillante para cachetes

# =============== Pusheen exacto - cada píxel contado de la imagen ===============
SPRITE_16 = [
    "          K         ",
    "         KDK        ",
    "        KDDDK       ",
    "       KDDDDK       ",
    "    K   KDDK   K    ",
    "   KDK   KK   KDK   ",
    "  KDDDK KKKK KDDDK  ",
    " KDDDKKKKKKKKKDDDDK ",
    " KGGGGGGGGGGGGGGGDK ",
    " KGGKGKGKGKGGGKGGGK ",
    "KGGGGGGGGGGGGGGGGGK ",
    "KGGPGGGGGGGGGGGPGGK ",
    "KGGGGGGKKKGGGGGGGGK ",
    "KGGGGGGKGKGGGGGGGGK ",
    "KGGGGGGGKGGGGGGGGGK ",
    "KGGGGGGGGGGGGGGGGGKKKK",
    " KGGGKGKGKGKGKGGGKDDK",
    " KGGKGKGKGKGKGKGGKDK",
    "  KKGKGKGKGKGKGKKDK",
    "    KKKKKKKKKKKK    "
]

def pixmap_to_surface(pattern, scale):
    h = len(pattern)
    w = len(pattern[0])
    surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)

    cmap = {' ': T, 'K': K, 'G': G, 'P': P, 'D': D}

    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            color = cmap.get(ch, T)
            if color[3] == 0:
                continue
            pygame.draw.rect(
                surf,
                color,
                (x*scale, y*scale, scale, scale)
            )
    return surf


def main():
    pygame.init()
    sprite = pixmap_to_surface(SPRITE_16, SCALE)

    # Ventana solo para ver el sprite
    win = pygame.display.set_mode((sprite.get_width(), sprite.get_height()))
    pygame.display.set_caption("Gatito pixel – vista frontal")

    # Guardar PNG con fondo transparente
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