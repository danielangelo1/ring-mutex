
from client_common import Client
import sys
import time


client_id, port, next_port = map(int, sys.argv[1:4])
client = Client(client_id, port, next_port)
print(f"Cliente {client_id}, {port}, {next_port} criado.")
time.sleep(5)
client.start_election()
