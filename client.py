# client.py

from client_common import Client
import sys

client_id, port, next_port = map(int, sys.argv[1:4])
client = Client(client_id, port, next_port)
print(f"Cliente {client_id}, {port}, {next_port} criado.")
