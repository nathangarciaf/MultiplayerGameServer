# Importar módulo de socket

from socket import *
import sys  # Para encerrar o programa

serverSocket = socket(AF_INET, SOCK_STREAM)

# Preparar um socket de servidor
# Fill in start
serverSocket.bind(('', 6789))
serverSocket.listen(1)
# Fill in end

while True:
    # Estabelecer a conexão
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()  # Fill in start, Fill in end

    try:
        message = connectionSocket.recv(1024)  # Fill in start, Fill in end
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()  # Fill in start, Fill in end

        # Enviar uma linha de cabeçalho HTTP para o socket
        # Fill in start
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        # Fill in end

        # Enviar o conteúdo do arquivo solicitado para o cliente
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())

        connectionSocket.close()
        
    except IOError:
        # Enviar mensagem de resposta para arquivo não encontrado
        # Fill in start
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        # Fill in end

        # Fechar o socket do cliente
        # Fill in start
        connectionSocket.close()
        # Fill in end

serverSocket.close()
sys.exit()  # Termina o programa após enviar os dados correspondentes