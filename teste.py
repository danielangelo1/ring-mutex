import random

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.next_process = None
        self.failed = False  # Indica se o processo falhou

    def set_next_process(self, next_process):
        self.next_process = next_process

    def simulate_failure(self, failure_rate=0.1):  # Reduzir a taxa de falha para 10%
        """Simula a falha de um processo com uma determinada taxa de falha."""
        return random.random() < failure_rate

    def start_election(self):
        print(f"Processo {self.pid} iniciou a eleição.")
        if not self.failed:
            self.send_election_message(self.pid)
        else:
            print(f"Processo {self.pid} falhou e não pode iniciar a eleição.")

    def send_election_message(self, election_id):
        if self.simulate_failure():
            print(f"Processo {self.pid} falhou durante a eleição.")
            self.failed = True
            # Tentar iniciar a eleição no próximo processo válido
            next_valid_process = self.next_process
            while next_valid_process.failed and next_valid_process != self:
                next_valid_process = next_valid_process.next_process
            next_valid_process.start_election()
            return

        max_id = max(self.pid, election_id)
        print(f"Processo {self.pid} enviando mensagem de eleição com ID {max_id} para o processo {self.next_process.pid}")
        self.next_process.receive_election_message(max_id)

    def receive_election_message(self, election_id):
        if self.failed:
            print(f"Processo {self.pid} falhou e não pode receber a mensagem.")
            # Não inicia nova eleição aqui para evitar loop infinito
            return

        if election_id == self.pid:
            print(f"Processo {self.pid} é o novo coordenador.")
            self.announce_coordinator(self.pid)
        else:
            self.send_election_message(election_id)

    def announce_coordinator(self, coord_id):
        if self.failed:
            return  # Processo falho não pode anunciar
        print(f"Processo {self.pid} anunciando o novo coordenador {coord_id}.")
        self.next_process.receive_coordinator_announcement(coord_id, self.pid)

    def receive_coordinator_announcement(self, coord_id, origin_id):
        if self.failed:
            return  # Processo falho não pode reconhecer
        if self.pid != origin_id:
            print(f"Processo {self.pid} reconhece o novo coordenador {coord_id}.")
            self.next_process.receive_coordinator_announcement(coord_id, origin_id)
        else:
            print(f"Processo {self.pid} concluiu o anúncio do coordenador.")

# Criando uma lista de processos
processes = [Process(i) for i in range(1, 6)]

# Configurando o próximo processo no anel
for i in range(len(processes)):
    processes[i].set_next_process(processes[(i + 1) % len(processes)])

# Iniciando a eleição
processes[0].start_election()
