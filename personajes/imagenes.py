import pygame

SCALE = 12   # tamaño de cada “pixel” en pantalla
OUT_PNG = "charco.png"  # puedes cambiar el nombre si quieres

# Paleta (RGBA)
# Espacio " " = Transparente
N = (0, 0, 0, 255)            # Negro (por si lo usas)
O = (128, 128, 128, 255)      # Gris oscuro
C = (192, 192, 192, 255)      # Gris claro
B = (255, 255, 255, 255)      # Blanco
R = (255, 182, 193, 255)      # Rosa

# Nuevos colores para el charco:
S_ = (153, 213, 242, 255)     # S = Azul suave (agua clara)
F_ = ( 86, 180, 233, 255)     # F = Azul más fuerte (pero no muy saturado)
T = (0, 0, 0, 0)              # Transparente

# =============== Sprite (charco) ===============
# Cada carácter representa un color de la paleta
# ' ' = T (transparente), 'S' = azul suave, 'F' = azul fuerte
# Mantén todas las filas con el mismo ancho para que no se recorte.


SPRITE = [
    "       SSSSSSSSS     ",
    "    SSSFFFFFFFFSS    ",
    "  SSFFFFFFFFFFFFFS   ",
    " SFFFFFFFFFFFFFFFFFS ",
    "SFFFFFFFFFFFFFFFFFFFS",
    "SFFFFFFFFFFFFFFFFFFFS",
    "SFFFFFSSFFFFFFFFFFFS ",
    " SSFFFSSSSFFFFFFFSS  ",
    "   SSSS    SSSSSS    "
]

def pixmap_to_surface(pattern, scale):
    h = len(pattern)
    w = len(pattern[0])
    # superficie con alpha para respetar transparencia
    surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)

    cmap = {
        " ": T, "N": N, "O": O, "C": C, "B": B, "R": R,
        "S": S_, "F": F_,
    }

    for y, row in enumerate(pattern):
        # por si alguna fila viene más corta, la rellenamos a la derecha
        row = row.ljust(w)
        for x, ch in enumerate(row):
            color = cmap.get(ch, T)
            if color[3] == 0:
                continue
            pygame.draw.rect(surf, color, (x*scale, y*scale, scale, scale))
    return surf


def main():
    pygame.init()
    sprite = pixmap_to_surface(SPRITE, SCALE)

    # Ventana para previsualizar el sprite
    win = pygame.display.set_mode((sprite.get_width(), sprite.get_height()))
    pygame.display.set_caption("Charco de agua – pixel art")

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
