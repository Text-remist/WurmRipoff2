import socket
import json
import threading
import random


# Example height map and tree map
def create_height_map(rows, cols, min_height=0, max_height=10):
    return [[random.randint(min_height, max_height) for _ in range(cols)] for _ in range(rows)]


def create_tree_map(rows, cols, tree_density=0.5):
    return [[random.random() < tree_density for _ in range(cols)] for _ in range(rows)]


def create_rock_map(rows, cols, rock_density=0.3):
    return [[random.random() < rock_density for _ in range(cols)] for _ in range(rows)]


def create_map(rows, cols, tile_density=0.5, min_value=1, max_value=3):
    # Generate the map using list comprehensions
    # For each row in the map
    return [
        # Create a list representing a row
        [
            # Generate a random value if a randomly generated number is less than tile_density, otherwise, generate 0
            random.randint(min_value, max_value) if random.random() < tile_density else 0
            # Repeat for each column in the row
            for _ in range(cols)
        ]
        # Repeat for each row
        for _ in range(rows)
    ]


# Generate maps
global height_map, tree_map, tile_map
height_map = create_height_map(20, 20)
tree_map = create_tree_map(20, 20)
rock_map = create_rock_map(20, 20)
tile_map = create_map(20, 20)
print(len(tree_map))
print(len(rock_map))
clients = []


def handle_client(conn):
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
        print(f"Connection aborted: {e}")
    except ConnectionResetError as e:
        print(f"Connection reset: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        if conn in clients:
            clients.remove(conn)



def process_update(update):
    global height_map, tree_map, tile_map

    if 'tree_chop' in update:
        x, y = update['tree_chop']
        tree_map[x][y] = False
        print("Tree Map Updated")
        print(tree_map)
        notify_clients()
    elif 'rock_smash' in update:
        x, y = update['rock_smash']
        rock_map[x][y] = False
        print("Rock Map Updated")
        print(rock_map)
        notify_clients()
    elif 'tile_change' in update:
        x, y, tile = update['tile_change']
        tile_map[x][y] = int(tile)
        print("Tile Map Updated")
        print(tile_map)
        notify_clients()


def notify_clients():
    global height_map, tree_map, tile_map
    data = json.dumps({'tree_map': tree_map, 'rock_map': rock_map, 'tile_map': tile_map})
    for client in clients:
        print()
        print(data)
        client.sendall(data.encode('utf-8'))


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('10.0.0.154', 5555))
    server.listen(5)

    print("Server started, waiting for clients...")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()
        print(tree_map)


if __name__ == "__main__":
    start_server()
