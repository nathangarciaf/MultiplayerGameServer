import socket
import select
import threading
import random

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 65432        # Porta que o servidor vai escutar
MAX_CLIENTS = 4     # Número máximo de clientes simultâneos 

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

def handle_client(client_socket, client_address, user_name):
    global secret_number, current_turn_index
    print(f'Iniciando processamento para {client_address} como usuário {user_name}')
    client_socket.sendall("VOCÊ ENTROU NO JOGO DE ADIVINHAÇÃO\n".encode())
    
    if len(clients) == 1:
        client_socket.sendall("Sua rodada. Jogue\n".encode())
    else:
        current_player = list(clients.values())[current_turn_index]
        client_socket.sendall(f'Rodada de usuário {current_player}\n'.encode())
    
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            
            message_decoded = message.decode('utf-8').strip()
            print(f'Recebido de {user_name}: {message_decoded}')
            
            if message_decoded.lower() == 'sair':
                print(f'Usuário {user_name} saiu do jogo.')
                client_socket.close()
                if client_socket in sockets_list:
                    sockets_list.remove(client_socket)
                if client_socket in clients:
                    del clients[client_socket]
                
                if clients:
                    client_names = list(clients.values())
                    print(client_names)
                    print("NOME DO USUÁRIO EM QUESTÃO: " + user_name)
                    print()
                    if user_name in client_names:
                        player_index = client_names.index(user_name)
                        print("IDX DO USUÁRIO EM QUESTÃO: " + player_index)
                        if player_index == current_turn_index:
                            current_turn_index = current_turn_index % (len(client_names) - 1) if len(client_names) > 1 else 0
                    
                    print(current_turn_index)
                    next_player = list(clients.keys())[current_turn_index]
                    print(next_player)
                    next_player.sendall("Sua rodada. Jogue\n".encode())
                    broadcast(f'Rodada de usuário {clients[next_player]}', next_player)
                return
            
            if message_decoded.upper().startswith("POST"):
                if clients[client_socket] == list(clients.values())[current_turn_index]:
                    try:
                        guess = int(message_decoded[5:].strip())
                    except ValueError:
                        client_socket.sendall("Jogada nao valida. Jogue novamente\n".encode())
                        continue
                    
                    if guess == secret_number:
                        broadcast(f'Usuário {user_name} acertou o número: {guess}. Nova rodada iniciando...')
                        secret_number = random.randint(1, 20)
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

    print(f'Servidor do Jogo iniciado. Escutando em {HOST}:{PORT}. Número secreto sorteado.')

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
                    
                    print(f'Nova conexão de {client_address} como {user_name}')
                    
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
