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
        self.coordinator = None
        self.election_in_progress = False

    def request_access(self, server_ip='localhost', server_port=12345):
        if self.coordinator != self.client_id:
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(f'request {self.client_id}'.encode())
                response = s.recv(1024).decode()
                if response == 'granted':
                    print(f"Cliente {self.client_id}: Acesso concedido. Entrando na seção crítica.")
                    hostname = os.popen('hostname').read().strip()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    s.sendall(f'write {self.client_id} {hostname} {timestamp}'.encode())
                    time.sleep(random.randint(1, 10))
                    print(f"Cliente {self.client_id}: Saindo da seção crítica.")
                    s.sendall(f'release {self.client_id}'.encode())
        except ConnectionRefusedError:
            print(f"Servidor não disponível. Cliente {self.client_id} iniciando eleição.")
            self.coordinator = None
            self.start_election()

    def set_next_client(self, next_client):
        self.next_client = next_client

    def simulate_failure(self, failure_rate=0.005):
        self.failed = random.random() < failure_rate
        return self.failed

    def start_election(self):
        if self.election_in_progress or self.failed:
            return
        self.election_in_progress = True
        self.send_election_message(self.client_id)

    def send_election_message(self, election_id):
       message = f"election {election_id}"

       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((self.next_client_add, self.next_client_port))
            print(f"Cliente {self.client_id} enviando mensagem de eleição com ID {election_id} para o próximo cliente.")
            s.sendall(message.encode())
        except ConnectionRefusedError:
            print(f"Cliente {self.client_id}: O próximo cliente não está disponível. Iniciando nova eleição.")
            self.start_election()


        if self.next_client:
            self.next_client.receive_election_message(election_id)

    def receive_election_message(self, election_id):
        if self.failed:
            if self.next_client:
                self.next_client.receive_election_message(election_id)
            return

        if election_id == self.client_id:
            print(f"Cliente {self.client_id} é o novo coordenador.")
            self.announce_coordinator(self.client_id)
            self.election_in_progress = False
        else:
            max_id = max(self.client_id, election_id)
            self.send_election_message(max_id)

    def announce_coordinator(self, coord_id):
        if self.failed or self.coordinator == coord_id:
            return
        self.coordinator = coord_id
        print(f"Cliente {self.client_id} anunciando o novo coordenador {coord_id}.")
        if self.next_client:
            self.next_client.receive_coordinator_announcement(coord_id, self.client_id)

    def receive_coordinator_announcement(self, coord_id, origin_id):
        if not self.failed:
            self.coordinator = coord_id
            print(f"Cliente {self.client_id} reconhece o novo coordenador {coord_id}.")
            if self.client_id != origin_id:
                if self.next_client:
                    self.next_client.receive_coordinator_announcement(coord_id, origin_id)
            else:
                print("Anúncio do coordenador completo.")
                self.request_access()
                self.election_in_progress = False

clientes = [Client(i) for i in range(1, 5)]  
for i in range(len(clientes)):
    next_index = (i + 1) % len(clientes)
    clientes[i].set_next_client(clientes[next_index])

clientes[0].start_election()