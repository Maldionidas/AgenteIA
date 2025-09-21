import pygame

SCALE = 12   # tamaño de cada “pixel” en pantalla
OUT_PNG = "raton.png"

# Paleta (RGBA)
# Espacio " " = Transparente
N = (0, 0, 0, 255)          # Negro (ojos)
O = (128, 128, 128, 255)    # Gris oscuro
C = (192, 192, 192, 255)    # Gris claro (cuerpo)
B = (255, 255, 255, 255)    # Blanco (vientre, orejas)
R = (255, 182, 193, 255)    # Rosa (nariz, patas, cola)
T = (0, 0, 0, 0)            # Transparente


# =============== Sprite 16x16 ===============
# Cada carácter representa un color de la paleta
#   ' ' = T, 'K' = negro, 'D' = gris oscuro, 'W' = blanco, 'G' = verde
# Diseño: cara frontal con hojita arriba, orejas negras, parches grises y ojitos
SPRITE_16 = [
    " OOO        OOO      ",
    "OCCCO      OCCCO     ",
    "OCBBCO    OCBBBCO    ",
    "OCBBCOOOOOCBBBBCO    ",
    "OCCBCCCCCCCCBBBCO    ",
    " OOOCCCCCCCCCCCO     ",
    "   NCCCNCCCCOOO      ",
    "  OCCCCCCCCO        R",
    " RCCCCCCCOCO       R ",
    "  OOOOOOOCCO       R ",
    "     OBBCCCO      R  ",
    "     OBBCCCCO     R  ",
    "    ROBBBRCCO     R  ",
    "    ROBBBRCCCO   R   ",
    "     OBBBCOCCO   R   ",
    "     OBBBCOCCO   R   ",
    "    RROOORROO RRR    "

]

def pixmap_to_surface(pattern, scale):
    h = len(pattern)
    w = len(pattern[0])
    surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)

    cmap = {
        " ": T, "N": N, "O": O,
        "C": C, "B": B, "R": R
    }

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
    pygame.display.set_caption("Ratón pixel – vista frontal")

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