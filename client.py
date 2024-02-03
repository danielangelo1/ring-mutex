import socket
import time
import sys
import random
import os

class Client:
    def __init__(self, client_id):
        self.client_id = client_id
        self.next_client = None
        self.failed = False

    def request_access(self, server_ip='localhost', server_port=12345):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            s.sendall(f'request {self.client_id}'.encode())
            response = s.recv(1024).decode()
            if response == 'granted':
                print(f"Cliente {self.client_id}: Acesso concedido. Entrando na seção crítica.")
                # Enviar mensagem para o servidor para modificar o arquivo
                hostname = os.popen('hostname').read().strip()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                s.sendall(f'write {self.client_id} {hostname} {timestamp}'.encode())
                time.sleep(random.randint(1, 10))  # Tempo aleatório na seção crítica
                print(f"Cliente {self.client_id}: Saindo da seção crítica.")
                s.sendall(f'release {self.client_id}'.encode())

    def set_next_client(self, next_client):
        self.next_client = next_client

    def simulate_failure(self, failure_rate=0.1):
        return random.random() < failure_rate

    def start_election(self):
        print(f"Cliente {self.client_id} iniciou a eleição.")
        if not self.failed:
            self.send_election_message(self.client_id)
        else:
            print(f"Cliente {self.client_id} falhou e não pode iniciar a eleição.")

    def send_election_message(self, election_id):
        if self.simulate_failure():
            print(f"Cliente {self.client_id} falhou durante a eleição.")
            self.failed = True
            if self.next_client:  # Verifica se há um próximo cliente antes de prosseguir
                next_valid_client = self.next_client
                while next_valid_client.failed and next_valid_client != self:
                    next_valid_client = next_valid_client.next_client
                next_valid_client.start_election()
            return
        
        max_id = max(self.client_id, election_id)
        print(f"Cliente {self.client_id} enviando mensagem de eleição com ID {max_id} para o cliente {self.next_client.client_id if self.next_client else 'N/A'}")
        if self.next_client:  # Garantir que existe um próximo cliente antes de enviar a mensagem
            self.next_client.receive_election_message(max_id)

    def receive_election_message(self, election_id):
        if self.failed:
            print(f"Cliente {self.client_id} falhou e não pode receber a mensagem.")
            return
        if election_id == self.client_id:
            print(f"Cliente {self.client_id} é o novo coordenador.")
            self.announce_coordinator(self.client_id)
        else:
            self.send_election_message(election_id)

    def announce_coordinator(self, coord_id):
        if self.failed:
            return
        print(f"Cliente {self.client_id} anunciando o novo coordenador {coord_id}.")
        if self.next_client:
            self.next_client.receive_coordinator_announcement(coord_id, self.client_id)

    def receive_coordinator_announcement(self, coord_id, origin_id):
        if self.failed:
            return
        if self.client_id != origin_id:
            print(f"Cliente {self.client_id} reconhece o novo coordenador {coord_id}.")
            self.next_client.receive_coordinator_announcement(coord_id, origin_id)
        else:
            print(f"Cliente {self.client_id} conclui o anuncio do coordernador {coord_id}.")

    def run(self):
        while True:
            try:
                self.request_access()
            except ConnectionRefusedError:
                print(f"Servidor não disponível. Iniciando eleição.")
                self.start_election()
                time.sleep(5)


if __name__ == "__main__":
    client_id = int(sys.argv[1])
    client = Client(client_id)
    client.run()