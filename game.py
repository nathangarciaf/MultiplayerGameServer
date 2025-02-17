import socket
import select
import threading
import random

# Configurações do servidor
HOST = '172.20.72.77'  # Endereço IP do servidor (localhost)
PORT = 1234             # Porta que o servidor vai escutar
MAX_CLIENTS = 4         # Número máximo de clientes simultâneos 

# Lista de clientes conectados
clients = {}
sockets_list = []
user_counter = 1  # Contador para nomeação de usuários

# Número secreto inicial
secret_number = random.randint(1, 20)
current_turn_index = 0  # Índice do jogador da vez

def broadcast(message, sender_socket=None):
    message += '\n'
    for client_socket in list(clients.keys()):
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode())
            except:
                client_socket.close()
                if client_socket in sockets_list:
                    sockets_list.remove(client_socket)
                if client_socket in clients:
                    del clients[client_socket]

def send_commands(client_socket):
    commands = (
        "Comandos disponíveis:\n"
        "post <valor>: dar o palpite em sua rodada\n"
        "get list: pegar a lista de jogadores\n"
        "sair: sair do jogo\n\n"
    )
    client_socket.sendall(commands.encode())

def handle_client(client_socket, client_address, user_name):
    global secret_number, current_turn_index
    print(f'Iniciando processamento para {client_address} como usuário {user_name}')
    
    # Enviar para o jogador seu nome e instruções
    client_socket.sendall(f"Seja bem-vindo ao Jogo, usuário {user_name}\nDê palpite do número entre 1 e 20\n\n".encode())
    send_commands(client_socket)  # Enviar a lista de comandos
    
    if len(clients) == 1:
        client_socket.sendall("Sua rodada. Jogue\n".encode())
    else:
        current_player = list(clients.values())[current_turn_index]
        client_socket.sendall(f'Rodada de usuário {current_player}\n'.encode())
    
    got_list_request = False  # Flag para controlar se o jogador pediu a lista

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            
            message_decoded = message.decode('utf-8').strip()
            print(f'Recebido de usuário {user_name}: {message_decoded}')
            
            if message_decoded.lower() == 'sair':
                print(f'Usuário {user_name} saiu do jogo.')
                # Fechar a conexão do cliente imediatamente
                client_socket.close()
                if client_socket in sockets_list:
                    sockets_list.remove(client_socket)
                if client_socket in clients:
                    del clients[client_socket]
                
                if clients:
                    client_names = list(clients.values())
                    if user_name in client_names:
                        player_index = client_names.index(user_name)
                        if player_index == current_turn_index:
                            current_turn_index = current_turn_index % (len(client_names) - 1) if len(client_names) > 1 else 0
                    
                    next_player = list(clients.keys())[current_turn_index]
                    next_player.sendall("Sua rodada. Jogue\n".encode())
                    broadcast(f'Rodada de usuário {clients[next_player]}', next_player)
                return  # Interrompe o loop e encerra o processo do cliente
                
            if message_decoded.upper().startswith("POST"):
                if clients[client_socket] == list(clients.values())[current_turn_index]:
                    try:
                        guess = int(message_decoded[5:].strip())
                    except ValueError:
                        client_socket.sendall("Jogada nao válida. Jogue novamente\n".encode())
                        continue
                    
                    if guess == secret_number:
                        broadcast(f'Usuário {user_name} acertou o número: {guess}. Nova rodada iniciando...')
                        secret_number = random.randint(1, 20)
                        print(f'Nova rodada iniciada! Número secreto sorteado: {secret_number}')
                        
                        current_turn_index = 0
                        first_player = list(clients.keys())[current_turn_index]

                        broadcast(f'Nova rodada! Rodada de usuário {clients[first_player]}')
                        first_player.sendall("Sua rodada. Jogue\n".encode())
                    else:
                        broadcast(f'Jogada de usuário {user_name} foi: {guess}, e estava incorreta.', client_socket)
                        client_socket.sendall("Jogada incorreta.\n".encode())
                        
                        if len(clients) > 1:
                            current_turn_index = (current_turn_index + 1) % len(clients)
                            next_player = list(clients.keys())[current_turn_index]
                            next_player.sendall("Sua rodada. Jogue\n".encode())
                            broadcast(f'Rodada de usuário {clients[next_player]}', next_player)
                        else:
                            client_socket.sendall("Sua rodada. Jogue\n".encode())
                else:
                    client_socket.sendall("Não é sua vez! Aguarde sua rodada.\n".encode())
            
            elif message_decoded.upper().startswith("GET"):
                player_list = "\n".join(list(clients.values()))
                client_socket.sendall(f"Lista de jogadores:\n{player_list}\n".encode())
            
        except ConnectionResetError:
            print(f'Conexão encerrada por {client_address} ({user_name})')
            break

def start_server():
    global user_counter, secret_number
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    sockets_list.append(server_socket)

    print(f'Servidor do Jogo iniciado. Escutando em {HOST}:{PORT}. Número secreto sorteado: {secret_number}')

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                if len(clients) < MAX_CLIENTS:
                    client_socket, client_address = server_socket.accept()
                    
                    user_name = f'{user_counter}'
                    user_counter += 1
                    
                    sockets_list.append(client_socket)
                    clients[client_socket] = user_name
                    
                    print(f'Nova conexão de {client_address} como usuário {user_name}')
                    
                    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, user_name))
                    client_thread.start()
                else:
                    print('Limite máximo de clientes atingido. Encerrando servidor.')
                    message = 'Limite de usuários ultrapassado! Servidor sendo fechado...\n'
                    broadcast(message)
                    for client_socket in list(clients.keys()):
                        client_socket.sendall(message.encode())
                        client_socket.close()
                    server_socket.close()
                    return
            else:
                try:
                    message = notified_socket.recv(1024)
                    if not message:
                        if notified_socket in sockets_list:
                            sockets_list.remove(notified_socket)
                        if notified_socket in clients:
                            del clients[notified_socket]
                        notified_socket.close()
                except:
                    continue
        
        for notified_socket in exception_sockets:
            if notified_socket in sockets_list:
                sockets_list.remove(notified_socket)
            if notified_socket in clients:
                del clients[notified_socket]
            notified_socket.close()

if __name__ == '__main__':
    start_server()
