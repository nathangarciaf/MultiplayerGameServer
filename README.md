# Jogo de Adivinhação - Servidor TCP

Este projeto implementa um servidor de jogo de adivinhação utilizando sockets TCP. 
O jogo permite que até 4 jogadores concorram para adivinhar um número secreto gerado aleatoriamente.

## Como Funciona o Jogo

O servidor sorteia um número secreto entre 1 e 20, assim os jogadores se conectam ao servidor e 
são atribuídos a uma ordem de jogo. O primeiro jogador da fila faz um palpite, se o palpite estiver correto, 
o jogo reinicia com um novo número secreto, porém caso o palpite estiver errado, a vez passa para o próximo jogador.
Jogadores podem sair a qualquer momento, sem que interfira na ordem de jogadas.

## Como Rodar

### Requisitos: 
Python 3 instalado na máquina

### Instruções: 
Clone ou baixe o repositório. De preferência, clone o repositóriocom o seguinte comando:
```
git clone https://github.com/nathangarciaf/MultiplayerGameServer
```

Execute o servidor com o comando, caso esteja no windows:
```
python game.py
```

Porém caso esteja usando Linux, pode ser que tenha que executar o comando:
```
python3 game.py
```
para executar o servidor.

### Como testar 
Para testar, abra um terminal para cada jogador e conecte-se usando Telnet:
```
telnet 127.0.0.1 1234
```

Envie palpites no formato:
```
POST <numero>
```
Caso estejam incorretos, espere sua rodada novamente ou espere um novo jogo caso
algum de seus adversários ganhe o jogo.

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

## Possíveis Melhorias

Interface Web: focando na melhora do quesito visual do jogo, facilitando a vizualização das adivinhações
e também dos jogadores que estão jogando o jogo.

Correção de pequenos bugs: Tive alguns problemas em questões envolvendo sair no meio do jogo fora da rodada,
e também problema com retornos ao servidor após sair do jogo uma vez

Multiplas Salas: Mais de uma sala possível para ser jogada o jogo.

Permitir maior quantidade de usuários: Atualmente o código está com o número limitado de usuários. A ideia
seria adicionar usuários de maneira dinâmica.