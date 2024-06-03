import random
import socket
import json
import threading
import time
class Client:
    def __init__(self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, 5555))
        self.tree_map = None
        self.rock_map = None
        self.tile_map = None
        self.my_player = None
        self.all_players = None
        self.lock = threading.Lock()
        self.start()

    def start(self):
        # Receive initial data
        data = self.client.recv(1000000)
        maps = json.loads(data.decode('utf-8'))
        self.tree_map = maps['tree_map']
        self.rock_map = maps['rock_map']
        self.tile_map = maps['tile_map']
        # Start a thread to listen for updates from the server
        threading.Thread(target=self.listen_for_updates).start()

        # Start a thread to simulate changes in data
        threading.Thread(target=self.simulate_changes).start()
    def listen_for_updates(self):
        buffer = ""
        while True:
            update = self.client.recv(1000000)
            if not update:
                break
            buffer += update.decode('utf-8')

            # Process all complete JSON objects in the buffer
            while True:
                try:
                    maps, idx = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[idx:].lstrip()  # Remove the processed object from the buffer
                    with self.lock:
                        if 'tree_map' in maps:
                            self.tree_map = maps['tree_map']
                        if 'rock_map' in maps:
                            self.rock_map = maps['rock_map']
                        if 'tile_map' in maps:
                            self.tile_map = maps['tile_map']
                        if 'my_player' in maps:
                            self.tile_map = maps['my_player']
                        if 'all_players' in maps:
                            self.tile_map = maps['all_players']

                except json.JSONDecodeError:
                    break  # Break the loop if no more complete JSON objects are found

    def simulate_changes(self):
        while True:
            time.sleep(1)  # Wait for 5 seconds before chopping another tree
            self.chop_tree(random.randint(0,19), random.randint(0,19))
            self.smash_rock(random.randint(0,19), random.randint(0,19))
            self.change_tile(random.randint(0,19), random.randint(0,19), random.randint(0,3))

    def chop_tree(self, x, y):
        with self.lock:
            if self.tree_map[x][y]:
                self.tree_map[x][y] = False
                update = json.dumps({'tree_chop': [x, y]})
                self.client.sendall(update.encode('utf-8'))
                print(f"Chopped tree at ({x}, {y})")

    def smash_rock(self, x, y):
        with self.lock:
            if self.rock_map[x][y]:
                self.rock_map[x][y] = False
                update = json.dumps({'rock_smash': [x, y]})
                self.client.sendall(update.encode('utf-8'))
                print(f"Smashed Rock at ({x}, {y})")

    def change_tile(self, x, y, tile):
        with self.lock:
            if self.tile_map[x][y] != tile:
                self.tile_map[x][y] = tile
                update = json.dumps({'tile_change': [x, y, tile]})
                self.client.sendall(update.encode('utf-8'))
                print(f"Changed Tile at ({x}, {y}) to {tile}")