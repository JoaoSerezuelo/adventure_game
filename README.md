# Jogo "Escolha Sua Própria Aventura" Cooperativo Multijogador

Este projeto implementa um jogo interativo do tipo "escolha sua própria aventura" com funcionalidade multijogador cooperativa e um chat em tempo real, utilizando a biblioteca RPyC para comunicação entre cliente e servidor.

## Requisitos

- Python 3.x
- Biblioteca RPyC

## Instalação

1.  **Clone ou baixe o repositório:**
    ```bash
    # Exemplo: git clone <url_do_repositorio>
    # Ou baixe os arquivos diretamente
    ```

2.  **Instale as biblioteca do projeto:**
    ```bash
    pip install -r requirements.txt
    ```

## Estrutura do Projeto

- `server.py`: Contém a lógica do servidor RPyC que gerencia o estado do jogo, as páginas da história, os votos dos jogadores e as mensagens do chat.
- `client.py`: Implementa o cliente RPyC que os jogadores utilizam para interagir com o jogo, visualizar a história, fazer escolhas, votar e conversar.
- `story_data.py`: Define a estrutura da história, incluindo páginas e opções de escolha.

## Como Executar

### 1. Iniciar o Servidor

Abra um terminal e execute o seguinte comando:

```bash
python server.py
```

O servidor será iniciado e aguardará conexões de clientes na porta `18861`.

### 2. Iniciar os Clientes

Abra um novo terminal para cada jogador e execute o cliente, fornecendo um nome de usuário:

```bash
python3 client.py Player1
```

Repita para cada jogador, substituindo `Player1` por um nome de usuário único (ex: `Player2`, `Player3`, etc.).

## Comandos do Cliente

Após se conectar ao servidor, o cliente exibirá a página atual da história, as opções de escolha, os votos atuais e as mensagens do chat. Você pode interagir com o jogo usando os seguintes comandos no prompt do cliente:

-   **Votar em uma escolha:** Digite o número da opção desejada (ex: `1` para a primeira opção).
-   **Enviar mensagem no chat:** Digite `chat <sua mensagem>` (ex: `chat Olá a todos, o que acham da opção 1?`).
-   **Avançar a página:** Digite `avancar`. A página só avançará se uma opção tiver a maioria dos votos.

## Estrutura da História (`story_data.py`)

O arquivo `story_data.py` contém um dicionário `STORY_PAGES` que define a história do jogo. Cada chave do dicionário é um ID de página, e o valor é outro dicionário com:

-   `"text"`: O texto da página da história.
-   `"choices"`: Uma lista de dicionários, onde cada um representa uma opção de escolha:
    -   `"text"`: O texto da opção.
    -   `"next_page"`: O ID da próxima página se esta opção for escolhida.

Você pode facilmente modificar ou expandir a história editando este arquivo.

## Considerações de Arquitetura

O projeto utiliza RPyC (Remote Python Call) para permitir a comunicação remota entre o servidor e os clientes. O servidor hospeda o estado central do jogo (página atual, chat, votos) e expõe métodos para que os clientes possam interagir. Os clientes, por sua vez, registram callbacks no servidor para receber atualizações em tempo real sobre mudanças na página, no chat e nos votos. Isso garante uma experiência multijogador dinâmica e cooperativa.

## Solução de Problemas

-   **`ConnectionRefusedError`**: Certifique-se de que o servidor (`server.py`) está em execução antes de iniciar qualquer cliente.
-   **`TimeoutError`**: Isso pode indicar um problema de rede ou que o servidor está sobrecarregado/bloqueado. Verifique o log do servidor para erros.
-   **Comportamento inesperado do terminal**: Em alguns ambientes, a limpeza de tela (`os.system("clear")`) pode causar problemas com o `input()`. Tente ajustar o cliente para não limpar a tela se isso ocorrer.

---

**Autor:** Manus AI
