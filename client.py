import socket
import time
import sys
import random
import os
import threading


class Client:
    def __init__(self, client_id, port, next_port):
        self.client_id = client_id
        self.next_client = None
        self.failed = False
        self.coordinator = None
        self.election_in_progress = False
        self.port = port
        self.next_client_port = next_port

        threading.Thread(target=self.listen_for_messages).start()

    def request_access(self):
        if self.coordinator is None or self.coordinator != self.client_id:
            print(f'\nCliente {self.client_id}: Solicitando acesso ao coordernador')

            self.send_request_to_coordinator()
        else:
            self.access_shared_resource()
    
    def send_request_to_coordinator(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', self.port))  
                s.sendall(f'request_access {self.client_id}'.encode())
                response = s.recv(1024).decode()
                if response == 'access_granted':
                    self.access_shared_resource()
                else:
                    print(f"Cliente {self.client_id}: Acesso negado ou em fila.")

        except ConnectionRefusedError:
            print(f"Cliente {self.client_id}: Coordenador não está disponível. Iniciando eleição.")
            self.start_election()

    def access_shared_resource(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 12345))
                s.sendall(f'request {self.client_id}'.encode())
                response = s.recv(1024).decode()
                if response == 'granted':
                    print(f"Cliente {self.client_id}: Acesso concedido. Entrando na seção crítica.")
                    hostname = os.popen('hostname').read()
                    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
                    s.sendall(f'write {self.client_id} {hostname} {timestamp}'.encode())
                    time.sleep(random.randint(1, 5)) 
                    print(f"Cliente {self.client_id}: Saindo da seção crítica.")
                    s.sendall(f'release {self.client_id}'.encode())
        except ConnectionRefusedError:
            print(f"Cliente {self.client_id}: Servidor do recurso compartilhado não disponível.")

    def set_next_client(self, next_client):
        self.next_client = next_client

    def simulate_failure(self, failure_rate=0.15):
        self.failed = random.random() < failure_rate
        return self.failed

    def start_election(self):
        if self.election_in_progress or self.failed:
            return
        self.election_in_progress = True
        print(f"\nCliente {self.client_id} iniciando eleição.")
        self.send_election_message(self.client_id)

    def listen_for_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            
            while True:
                conn, addr = s.accept()
                
                with conn:
                    data = conn.recv(1024).decode()
                    parts = data.split()
                    if parts[0] == 'election':
                        election_id = int(parts[1])
                        print(f"Cliente {self.client_id} recebeu mensagem de eleição com ID {election_id}.")
                        self.receive_election_message(election_id)
                    elif parts[0] == 'coordinator':
                        coord_id = int(parts[1])
                        print(f"Cliente {self.client_id} recebeu anúncio de novo coordenador {coord_id}.")
                        self.receive_coordinator_announcement(coord_id, int(parts[2]))
                    elif parts[0] == 'request_access':
                        if self.failed:
                            conn.sendall(b'access_denied')
                        else:
                            conn.sendall(b'access_granted')

    def send_election_message(self, election_id):
    #    if self.simulate_failure():
    #           print(f"Cliente {self.client_id} falhou ao enviar mensagem de eleição.")
    #           self.election_in_progress = False
    #           self.start_election()
    #           return

       message = f"election {election_id}"
       
       print(f"Cliente {self.client_id} enviando mensagem de eleição com ID {election_id} para o próximo cliente.")
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('localhost', self.next_client_port))
            s.sendall(message.encode())
        except ConnectionRefusedError:
            print(f"Cliente {self.client_id}: O próximo cliente não está disponível. Iniciando nova eleição.")
            self.election_in_progress = False
            self.start_election()



        if self.next_client:
            self.next_client.receive_election_message(election_id)

    def receive_election_message(self, election_id):
        if election_id == self.client_id:
            self.announce_coordinator(self.client_id)
        elif election_id > self.client_id:
            self.send_election_message(election_id)
        else:
            self.send_election_message(self.client_id)

    def announce_coordinator(self, coord_id):
        if self.failed or self.coordinator == coord_id:
            return
        self.coordinator = coord_id

        print(f"\nCliente {self.client_id} anunciando o novo coordenador {coord_id}.")
        if self.next_client:
            self.next_client.receive_coordinator_announcement(coord_id,self.client_id)

    def receive_coordinator_announcement(self, coord_id, origin_id):
        if not self.failed:
            self.coordinator = coord_id
            print(f"Cliente {self.client_id} reconhece o novo coordenador {coord_id}.")
            if self.client_id != origin_id:
                if self.next_client:
                    self.next_client.receive_coordinator_announcement(coord_id,  origin_id)
            else:
                print("Anúncio do coordenador completo.")
                self.election_in_progress = False

    def random_access_request(self):
        time.sleep(random.randint(1, 10))
        self.request_access()

client_id, port, next_port = map(int, sys.argv[1:4])
client = Client(client_id, port, next_port)
print(f"Cliente {client_id}, {port}, {next_port} criado.")

randomNum = random.randint(0, 4)
print(f"{randomNum}")
time.sleep(5)

if client_id == randomNum:
    print(f"Cliente {client_id}.")
    client.start_election()

time.sleep(10)
client.random_access_request()
