import socket
import threading

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Server rodando em {host}:{port}")

    def handle_client(self, client_socket):
        client_id = None
        lock_acquired = False
        try:
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    parts = data.decode().split()
                    if len(parts) >= 2:
                        command = parts[0]
                        client_id = parts[1]
                        if command == 'request':
                            self.lock.acquire()
                            print(f"Cliente {client_id} recebeu acesso à seção crítica.")
                            client_socket.sendall(b'granted')
                        elif command == 'release':
                            self.lock.release()
                            print(f"Cliente {client_id} liberou a seção crítica.")
                            client_socket.sendall(b'released')
                        elif command == 'write':
                            self.write_file(parts[1:])
                    else:
                        print("Mensagem inválida recebida")
        except ConnectionResetError:
            print(f"A conexão com o cliente {client_id} foi inesperadamente fechada.")
            if self.lock.locked():
                self.lock.release()

    def write_file(self, data):
        with open('resource.txt', 'a') as f:
            f.write(f"{' '.join(data)}\n")
            print(f"Cliente {data[0]} escreveu no arquivo")

    def run(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            # print(f"Conexão de {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()


    


if __name__ == "__main__":
    server = Server()
    server.run()
