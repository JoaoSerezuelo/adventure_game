# Adventure Game

Um jogo de aventura multijogador desenvolvido em Python.

## Sobre o Jogo

Este é um jogo de aventura baseado em rede, onde um jogador atua como o servidor (Host) e outros jogadores podem se conectar como clientes para participar da mesma aventura.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

* [Python](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads) (para clonar o repositório)
* Um software de VPN para simulação de LAN, como o [Radmin VPN](https://www.radmin-vpn.com/br/).

## Instalação

1.  Abra seu terminal ou prompt de comando.
2.  Clone este repositório:
    ```sh
    git clone [https://github.com/JoaoSerezuelo/adventure_game.git](https://github.com/JoaoSerezuelo/adventure_game.git)
    ```
3.  Navegue até a pasta do projeto:
    ```sh
    cd adventure_game
    ```
4.  Instale as dependências Python necessárias:
    ```sh
    pip install -r requirements.txt
    ```

## Como Jogar

Para jogar este jogo, uma pessoa deve ser o **Host (Servidor)** e os outros jogadores serão os **Clientes**.

### 1. Configuração da Rede (Para todos os jogadores)

Como este jogo é projetado para ser jogado em uma rede local (LAN), vocês precisarão usar um software de VPN para simular uma.

1.  Baixe e instale o Radmin VPN (ou similar).
2.  O jogador Host deve ir em "Criar Rede", definir um nome e senha, e compartilhar essas credenciais com os outros jogadores.
3.  Os outros jogadores devem ir em "Entrar na Rede" e usar as credenciais fornecidas.
4.  Após todos entrarem, o Host deve copiar o seu próprio endereço de IP de dentro do Radmin VPN (Ex: `26.XXX.XXX.XXX`).

### 2. Para o Host (Servidor)

1.  Abra o terminal (na pasta do projeto).
2.  Inicie o servidor:
    ```sh
    python server.py
    ```
3.  Envie o seu endereço IP do Radmin VPN (obtido na Etapa 1) para os outros jogadores.

### 3. Para os Clientes (Jogadores)

1.  **IMPORTANTE:** Antes de iniciar o jogo, abra o arquivo `client.py` com um editor de texto.
2.  Na **linha 32** (ou onde estiver indicado), você encontrará uma variável de IP.
3.  **Altere o endereço de IP** para o endereço IP do Host (o IP obtido do Radmin VPN).

    *Exemplo em `client.py` (linha 32):*
    ```python
    # Altere este IP para o IP do Radmin VPN do Host
    host = "26.66.56.226" 
    ```

4.  Salve o arquivo `client.py`.
5.  Abra o terminal (na pasta do projeto) e inicie o cliente:
    ```sh
    python client.py
    ```

6.  Divirta-se!