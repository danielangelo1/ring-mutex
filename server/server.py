import socket
import threading
import queue
import time

def handle_client(connection, address, access_queue):
    try:
        while True:
            message = connection.recv(1024).decode()
            if message == 'REQUEST_ACCESS':
                access_queue.put((connection, address))
                break
    finally:
        connection.close()
        print(f"Connection with {address} closed")

def access_manager(access_queue, shared_file):
    while True:
        connection, address = access_queue.get()
        print(f"Access requested by {address}")
        # Simula o acesso ao arquivo
        with open(shared_file, 'a') as file:
            file.write(f"{address} accessed at {time.ctime()}\n")
        connection.sendall(b'ACCESS_GRANTED')
        access_queue.task_done()
        print(f"Access granted to {address}")

def main():
    host = '0.0.0.0'
    port = 12345
    access_queue = queue.Queue()
    shared_file = '/shared_file.txt'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    threading.Thread(target=access_manager, args=(access_queue, shared_file)).start()

    print("Server is listening...")

    while True:
        client_connection, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_connection, client_address, access_queue)).start()

if __name__ == '__main__':
    main()
    



