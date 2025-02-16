import socket
import select
import threading

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 65432        # Porta que o servidor vai escutar
MAX_CLIENTS = 3     # Número máximo de clientes simultâneos

# Função para processar dados em uma thread separada
def handle_client(client_socket, client_address):
    print(f'Iniciando processamento para {client_address}')
    
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print(f'Conexão encerrada por {client_address}')
                break

            message_decoded = message.decode()
            print(f'Recebido de {client_address}: {message_decoded}')
            
            if message_decoded.strip().lower() == 'fim':
                print(f'Encerrando conexão com {client_address} devido à palavra-chave "fim".')
                break
            
            # Aqui poderia ser feita uma operação mais pesada
            response = f'Eco: {message_decoded}'
            client_socket.sendall(response.encode())
        
        except ConnectionResetError:
            print(f'Conexão foi forçada a encerrar por {client_address}')
            break

    client_socket.close()

# Função principal para iniciar o servidor
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    sockets_list = [server_socket]
    clients = {}
    threads = []

    print(f'Servidor iniciado e escutando em {HOST}:{PORT}')

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                if len(clients) < MAX_CLIENTS:
                    client_socket, client_address = server_socket.accept()
                    
                    sockets_list.append(client_socket)
                    clients[client_socket] = client_address
                    
                    print(f'Nova conexão de {client_address}')
                    
                    # Cria uma thread para lidar com o cliente
                    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                    client_thread.start()
                    threads.append(client_thread)
                else:
                    print('Limite máximo de clientes atingido. Recusando nova conexão.')
                    client_socket, client_address = server_socket.accept()
                    client_socket.sendall(b'Servidor cheio. Tente novamente mais tarde.')
                    client_socket.close()
            else:
                # Apenas mantém a conexão ativa no select para evitar que ela seja desconectada
                try:
                    message = notified_socket.recv(1024)
                    if not message:
                        print(f'Conexão encerrada por {clients[notified_socket]}')
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]
                        notified_socket.close()
                except:
                    continue
        
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
            notified_socket.close()

    # Garante que todas as threads sejam encerradas corretamente
    for t in threads:
        t.join()

if __name__ == '__main__':
    start_server()
