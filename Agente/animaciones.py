import pygame
from config import TAM

class Animaciones:
    def __init__(self, raton_img_path="personajes/raton.png"):
        self.animando = False
        self.inicio = 0
        self.duracion = 1000  # 1 segundo
        raton_size = int(TAM * 0.4)
        self.raton_img = pygame.transform.scale(
            pygame.image.load(raton_img_path).convert_alpha(),
            (raton_size, raton_size)
        )
    def iniciar(self):
        self.animando = True
        self.inicio = pygame.time.get_ticks()

    def actualizar(self):
        if self.animando and pygame.time.get_ticks() - self.inicio >= self.duracion:
            self.animando = False
            return True  # terminó la animación
        return False
        