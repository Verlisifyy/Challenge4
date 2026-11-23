from pathlib import Path

import pygame


class Entity:
    def __init__(self, x, y, width, height, velocity):
        self.rect = pygame.Rect(x, y, width, height)
        self.y = float(y)
        self.velocity = velocity

    def update(self, delta_time, screen_height):
        self.y += self.velocity * delta_time

        if self.rect.height >= screen_height:
            self.y = 0
            self.velocity = 0
        elif self.y < 0:
            self.y = 0
            self.velocity = abs(self.velocity)
        elif self.y + self.rect.height > screen_height:
            self.y = screen_height - self.rect.height
            self.velocity = -abs(self.velocity)

        self.rect.y = round(self.y)


pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
sprite = pygame.image.load(
    str(Path(__file__).with_name("flappy.jpg"))
).convert()
sprite = pygame.transform.scale(sprite, (48, 48))
entity = Entity(100, 250, sprite.get_width(), sprite.get_height(), 180)

running = True
while running:
    delta_time = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    entity.update(delta_time, screen.get_height())

    screen.fill((135, 206, 235))
    screen.blit(sprite, entity.rect)
    pygame.display.flip()

pygame.quit()


