import pygame
import random
import threading
import time
from client import Client

# Define colors
GRASS = (17, 124, 19)
DIRT = (118, 85, 43)
STONE = (89, 89, 89)

# Define tile size and screen size
TILE_SIZE = 30
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

class Player:
    def __init__(self, server_ip, x, y):
        self.client = Client(server_ip)
        self.running = False
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.tile_images = {
            0: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            1: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            2: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            3: pygame.Surface((TILE_SIZE, TILE_SIZE))
        }
        self.tile_images[0].fill(GRASS)
        self.tile_images[1].fill((17, 124, 19))
        self.tile_images[2].fill(DIRT)
        self.tile_images[3].fill(STONE)
        self.username = "john"
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last_move_time = 0
        self.cooldown = 0.2
        self.vel = 1

    def move(self):
        current_time = time.time()
        if current_time - self.last_move_time < self.cooldown:
            return  # Exit the method if still in cooldown period

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel
            self.last_move_time = current_time  # Update last move time

        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - TILE_SIZE - self.vel:
            self.x += self.vel
            self.last_move_time = current_time  # Update last move time

        if keys[pygame.K_UP] and self.y > self.vel:
            self.y -= self.vel
            self.last_move_time = current_time  # Update last move time

        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - TILE_SIZE - self.vel:
            self.y += self.vel
            self.last_move_time = current_time  # Update last move time

        self.update()

    def update(self):
        self.rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def start(self):
        self.running = True
        self.run_display()

    def run_display(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.move()
            self.draw_map()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def draw_map(self):
        # Draw tiles
        tile_map = self.client.tile_map
        for x in range(len(tile_map)):
            for y in range(len(tile_map[0])):
                tile_id = tile_map[x][y]
                self.screen.blit(self.tile_images[tile_id], (x * TILE_SIZE, y * TILE_SIZE))

        # Draw player
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect)  # Draw the player's rect
        font = pygame.font.SysFont("Arial", 30)
        text_surface = font.render(self.username, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.rect.centerx, self.rect.top - 20)
        self.screen.blit(text_surface, text_rect)
        print(self.x)
        print(self.y)

if __name__ == "__main__":
    game = Player("169.254.158.91", 0, 0)
    game.start()
