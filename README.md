# Jogo de Adivinhação - Servidor TCP

Este projeto implementa um servidor de jogo de adivinhação utilizando sockets TCP. 
O jogo permite que até 4 jogadores concorram para adivinhar um número secreto gerado aleatoriamente.

## Como Funciona o Jogo

O servidor sorteia um número secreto entre 1 e 20, assim os jogadores se conectam ao servidor e 
são atribuídos a uma ordem de jogo. O primeiro jogador da fila faz um palpite, se o palpite estiver correto, 
o jogo reinicia com um novo número secreto, porém caso o palpite estiver errado, a vez passa para o próximo jogador.
Jogadores podem sair a qualquer momento, sem que interfira na ordem de jogadas.

## Como Rodar

Requisitos: Python 3 instalado na máquina

Instruções:

Clone ou baixe o repositório. De preferência, clone o reposótio com o seguinte comando:
```
git clone https://github.com/nathangarciaf/MultiplayerGameServer
```

Execute o servidor com o comando:
```
python game.py
```
Caso esteja no windows, porém caso esteja usando Linux, pode ser que tenha que executar o comando:
```
python game.py
```
para executar o servidor.


Para testar, abra um terminal para cada jogador e conecte-se usando Telnet:
```

telnet 127.0.0.1 65432
```

Envie palpites no formato:
```
POST <numero>
```

Exemplo:
```
POST 10
```
Para sair do jogo, digite:
```
sair
```

## Relatório de Escolhas de Implementação

Sockets TCP: Escolhido para conexões confiáveis entre os jogadores e o servidor.

Threads: Cada jogador tem uma thread para tratar mensagens de forma independente.

Select: Utilizado para monitorar conexões ativas e tratar comunicação eficiente.

Gerenciamento de turnos: Mantemos uma lista de jogadores para garantir a ordem correta dos turnos.

Recuperação de saída de jogadores: Se um jogador sai, o turno passa para o próximo automaticamente.

Este projeto proporciona uma experiência multiplayer simples via terminal, ilustrando conceitos de redes e sincronização entre clientes.