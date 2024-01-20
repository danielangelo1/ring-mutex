import socket
import threading
import os

def initiate_election(id, nodes):
    election_message = f'ELECTION {id}'
    next_node = (id + 1) % len(nodes)
    send_message_to_node(election_message, nodes[next_node])

def send_message_to_node(message, node):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(node)
        sock.sendall(message.encode())

def handle_messages(id, nodes):
    host, port = nodes[id]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen()
        while True:
            conn, _ = sock.accept()
            message = conn.recv(1024).decode()
            if message.startswith('ELECTION'):
                process_election_message(id, nodes, message)

def process_election_message(id, nodes, message):
    _, origin_id = message.split()
    origin_id = int(origin_id)

    if origin_id == id:
        # This node is the new coordinator
        # Announce to the network
        announce_coordinator(id, nodes)
    elif origin_id > id:
        # Pass the election message on
        next_node = (id + 1) % len(nodes)
        send_message_to_node(message, nodes[next_node])

def announce_coordinator(id, nodes):
    for node in nodes:
        if node != nodes[id]:
            send_message_to_node(f'COORDINATOR {id}', node)

def main():
    # Configuração de nós para ambiente Docker
    nodes = {
        0: ('client1', 5000),
        1: ('client2', 5001),
        2: ('client3', 5002),
        3: ('client4', 5003)
    }

    my_id = int(os.getenv('NODE_ID', 0))


    if my_id not in nodes:
        print(f"ID do nó inválido: {my_id}")
        return
    
    threading.Thread(target=handle_messages, args=(my_id, nodes)).start()



if __name__ == '__main__':
    main()