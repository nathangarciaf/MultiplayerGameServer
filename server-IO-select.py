import socket
import select

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 65432        # Porta que o servidor vai escutar

# Função principal para iniciar o servidor
def start_server():
    # Criação do socket principal
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    # Lista de sockets que o select deve monitorar
    sockets_list = [server_socket]
    
    # Dicionário para armazenar os endereços dos clientes
    clients = {}

    print(f'Servidor iniciado e escutando em {HOST}:{PORT}')

    while True:
        # Chama select para monitorar os sockets listados
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            # Novo cliente tentando se conectar
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                
                print(f'Nova conexão de {client_address}')
            
            # Cliente enviando uma mensagem
            else:
                message = notified_socket.recv(1024)
                
                if not message:
                    # Conexão foi encerrada pelo cliente
                    print(f'Conexão encerrada por {clients[notified_socket]}')
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()
                    continue
                
                # Processa a mensagem
                client_address = clients[notified_socket]
                message_decoded = message.decode()
                print(f'Recebido de {client_address}: {message_decoded}')
                
                if message_decoded.strip().lower() == 'fim':
                    print(f'Encerrando conexão com {client_address} devido à palavra-chave "fim".')
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()
                else:
                    # Ecoa a mensagem de volta ao cliente
                    notified_socket.sendall(message)
        
        # Trata qualquer exceção em sockets monitorados
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
            notified_socket.close()

if __name__ == '__main__':
    start_server()
