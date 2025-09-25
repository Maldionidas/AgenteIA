import pygame

# --- Clase Energia ---
class Energia:
    def __init__(self,energia_max=200,recarga_por_segundo=10,costo_paso=1):
        # Energía
        self.energia_max = energia_max
        self.valor = energia_max
        self.costo_paso = costo_paso
        self.recarga_por_segundo = recarga_por_segundo
        self.ultimo_tick = pygame.time.get_ticks()
        
    def consumir(self):
        if self.valor > 0:
            self.valor = max(0, self.valor - self.costo_paso)

    def recargar(self, objetivo):
        ahora = pygame.time.get_ticks()
        delta_ms = ahora - self.ultimo_tick
        recarga = (delta_ms / 1000) * self.recarga_por_segundo
        self.valor = min(objetivo, self.valor + recarga)
        self.ultimo_tick = ahora