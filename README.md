# TP 2 - Sistemas distribuidos

Este projeto implementa um sistema distribuído para a gestão de eleições e exclusão mútua utilizando algoritmos de eleição do anel e exclusão mútua centralizada.

## Funcionalidades

- **Exclusão Mútua Centralizada**: Garante que apenas um cliente por vez possa acessar o recurso compartilhado.
- **Algoritmo de Eleição do Anel**: Define dinamicamente um coordenador (líder) entre os dispositivos no sistema distribuído.
- **Recuperação de Falhas**: Inicia automaticamente uma nova eleição caso o coordenador atual falhe ou se desconecte.
- **Acesso ao Recurso Compartilhado**: Modifica um arquivo centralizado no servidor com o hostname e o timestamp do acesso.

## Configuração

### Dependências

- Python 3.x
- Bibliotecas Python: `socket`, `threading`, `time`, `os`, `random`

### Execução

1. Tenha o Docker e o Docker Compose instalados.
2. Execute o comando `docker-compose up --build` na raiz do projeto.
3. O servidor e os clientes serão inicializados.

## Estrutura do Projeto

- `client.py`: Lógica do cliente, incluindo solicitação de acesso ao recurso e participação na eleição.
- `server.py`: Servidor que gerencia o acesso ao recurso compartilhado e coordena as eleições.
- `resource.txt`: Arquivo de recurso compartilhado que os clientes modificam.
- `Dockerfile` e `docker-compose.yml`: Configurações para containerização e simulação de ambiente distribuído.

## Autores

- [Daniel Ângelo]
- [Arthur Feu]
