import socket
import json
import threading
import random
from player import Player
import time
from server_gui import ServerGui


# Example height map and tree map
def create_height_map(rows, cols, min_height=0, max_height=10):
    return [[random.randint(min_height, max_height) for _ in range(cols)] for _ in range(rows)]


def create_tree_map(rows, cols, tree_density=0.5):
    return [[random.random() < tree_density for _ in range(cols)] for _ in range(rows)]


def create_rock_map(rows, cols, rock_density=0.3):
    return [[random.random() < rock_density for _ in range(cols)] for _ in range(rows)]


def create_map(rows, cols, tile_density=0.5, min_value=1, max_value=3):
    return [
        [random.randint(min_value, max_value) if random.random() < tile_density else 0
         for _ in range(cols)] for _ in range(rows)
    ]


# Generate maps

height_map = create_height_map(20, 20)
tree_map = create_tree_map(20, 20)
rock_map = create_rock_map(20, 20)
tile_map = create_map(20, 20)

def save(data_list, filename_list):
    """Saves each item in data_list to the corresponding file in filename_list."""
    for data, filename in zip(data_list, filename_list):
        with open(filename, "w") as file:
            json.dump(data, file)
            print(f"File: {filename} is saved.")
'''
data_list = []
filename_list = []
data_list.append(height_map)
data_list.append(tree_map)
data_list.append(rock_map)
data_list.append(tile_map)
filename_list.append("./json/height_map.json")
filename_list.append("./json/tree_map.json")
filename_list.append("./json/rock_map.json")
filename_list.append("./json/tile_map.json")
save(data_list,filename_list)
'''
def load_json_as_list(filename):
    """Load data from a JSON file and return it as a list."""
    with open(filename, "r") as file:
        data = json.load(file)
    return data


# Load each JSON file into a list
height_map = load_json_as_list("./json/height_map.json")
tree_map = load_json_as_list("./json/tree_map.json")
rock_map = load_json_as_list("./json/rock_map.json")
tile_map = load_json_as_list("./json/tile_map.json")



def append_save_files():
    data_list = []
    filename_list = []
    data_list.append(height_map)
    data_list.append(tree_map)
    data_list.append(rock_map)
    data_list.append(tile_map)
    filename_list.append("./json/height_map.json")
    filename_list.append("./json/tree_map.json")
    filename_list.append("./json/rock_map.json")
    filename_list.append("./json/tile_map.json")
    return data_list, filename_list


clients = []
lock = threading.Lock()


def handle_client(conn, player_index):
    global height_map, tree_map, tile_map, rock_map, clients

    try:
        # Send initial data
        data = json.dumps({'tree_map': tree_map, 'rock_map': rock_map, 'tile_map': tile_map})
        conn.sendall(data.encode('utf-8'))

        buffer = ""
        while True:
            update = conn.recv(1000000)
            if not update:
                break
            buffer += update.decode('utf-8')

            # Process all complete JSON objects in the buffer
            while True:
                try:
                    update_json, idx = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[idx:].lstrip()  # Remove the processed object from the buffer
                    process_update(update_json)
                except json.JSONDecodeError:
                    break  # Break the loop if no more complete JSON objects are found

    except ConnectionAbortedError as e:
        data_list, filename_list = append_save_files()
        save(data_list, filename_list)
        print(f"Connection aborted: {e}")
    except ConnectionResetError as e:
        data_list, filename_list = append_save_files()
        save(data_list, filename_list)
        print(f"Connection reset: {e}")
    except Exception as e:
        data_list, filename_list = append_save_files()
        save(data_list, filename_list)
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        with lock:
            if conn in clients:
                clients.remove(conn)


def process_update(update):
    global height_map, tree_map, tile_map, rock_map

    if 'tree_chop' in update:
        x, y = update['tree_chop']
        with lock:
            tree_map[x][y] = False
    elif 'rock_smash' in update:
        x, y = update['rock_smash']
        with lock:
            rock_map[x][y] = False
    elif 'tile_change' in update:
        x, y, tile = update['tile_change']
        with lock:
            tile_map[x][y] = int(tile)

    notify_clients()


def notify_clients():
    global height_map, tree_map, tile_map, rock_map
    data = json.dumps({'tree_map': tree_map, 'rock_map': rock_map, 'tile_map': tile_map})
    with lock:
        for client in clients:
            client.sendall(data.encode('utf-8'))


def start_server():
    run = True

    # Run the GUI in a separate thread
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('169.254.158.91', 5555))
    server.listen(5)
    print("Server started, waiting for clients...")
    data_list, filename_list = append_save_files()
    save(data_list, filename_list)
    while run:
        conn, addr = server.accept()
        print(f"Computer {addr} joined the server.")
        time.sleep(1)
        clients.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn, len(clients) - 1))
        client_thread.start()


if __name__ == "__main__":
    start_server()
