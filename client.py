import socket
import time
import sys
import random
import os

def request_access(client_id, server_ip='localhost', server_port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        s.sendall(f'request {client_id}'.encode())
        response = s.recv(1024).decode()
        if response == 'granted':
            print(f"Cliente {client_id}: Acesso concedido. Entrando na seção crítica.")
            # Enviar mensagem para o servidor para modificar o arquivo
            hostname = os.uname()[1]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            s.sendall(f'write {client_id} {hostname} {timestamp}'.encode())
            time.sleep(random.randint(1, 10))  # Tempo aleatório na seção crítica
            print(f"Cliente {client_id}: Saindo da seção crítica.")
            s.sendall(f'release {client_id}'.encode())

if __name__ == "__main__":
    client_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    request_access(client_id)