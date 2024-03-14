import pygame
from network import Network


class LanMultiplayer:
    def run(self):
        running = True
        n = Network()
        p = n.getP()
        clock = pygame.time.Clock()
        while running:
            clock.tick(60)
            p2 = n.send(p)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

            p.move()
            p.update()
