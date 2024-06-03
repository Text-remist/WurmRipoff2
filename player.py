import pygame
import random
import threading
import time
from client import Client

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

# Define tile size and screen size
TILE_SIZE = 30
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

class Game:
    def __init__(self, server_ip):
        self.client = Client(server_ip)
        self.running = False
        self.tile_images = {
            0: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            1: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            2: pygame.Surface((TILE_SIZE, TILE_SIZE)),
            3: pygame.Surface((TILE_SIZE, TILE_SIZE))
        }
        self.tile_images[0].fill(	(19,109,21))
        self.tile_images[1].fill((17,124,19))
        self.tile_images[2].fill(	(19,133,16))
        self.tile_images[3].fill(	(38,139,7))
        self.game_thread = None

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Display")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_thread = threading.Thread(target=self.simulate_game)
        self.game_thread.start()
        self.run_display()

    def run_display(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    if self.game_thread:
                        self.game_thread.join()
            self.draw_map()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def draw_map(self):
        tile_map = self.client.tile_map
        for x in range(len(tile_map)):
            for y in range(len(tile_map[0])):
                tile_id = tile_map[x][y]
                self.screen.blit(self.tile_images[tile_id], (x * TILE_SIZE, y * TILE_SIZE))

    def simulate_game(self):
        while self.running:
            time.sleep(1)  # Simulate game ticks every 1 second
            # Simulate player actions
            action = random.choice(["chop_tree", "smash_rock", "change_tile"])
            if action == "chop_tree":
                x, y = random.randint(0, 19), random.randint(0, 19)
                self.client.chop_tree(x, y)
            elif action == "smash_rock":
                x, y = random.randint(0, 19), random.randint(0, 19)
                self.client.smash_rock(x, y)
            elif action == "change_tile":
                x, y, tile = random.randint(0, 19), random.randint(0, 19), random.randint(0, 3)
                self.client.change_tile(x, y, tile)

if __name__ == "__main__":
    server_ip = input("ENTER SERVER IP: ")
    game = Game(server_ip)
    game.start()

