import socket
import threading

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 65433        # Porta que o servidor vai escutar

# Função para lidar com um cliente
def handle_client(conn, addr):
    print(f'Conectado a {addr}')
    
    # Loop para manter a conexão com o cliente
    with conn:
        while True:
            data = conn.recv(1024)  # Recebe os dados do cliente
            if not data:
                break  # Se não receber dados, encerra a conexão
            
            message = data.decode()
            print(f'Recebido de {addr}: {message}')
            
            if message.strip().lower() == 'fim':
                print(f'Encerrando conexão com {addr} devido à palavra-chave "fim".')
                break  # Encerra a conexão se a string "fim" for recebida

            conn.sendall(data)  # Envia de volta os dados recebidos (echo)

    print(f'Conexão encerrada com {addr}')

# Função principal para iniciar o servidor
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Servidor iniciado e escutando em {HOST}:{PORT}')
        
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f'Número de threads ativas: {threading.active_count() - 1}')  # Desconta a thread principal

if __name__ == '__main__':
    start_server()
