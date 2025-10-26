import rpyc
import threading
import sys
import time
import os
import json # Importa a biblioteca JSON

class StoryGameClient(rpyc.Service):
    def __init__(self, username):
        self.username = username
        self.conn = None
        self.game_service = None
        self.current_page_id = None
        self.current_page_data = None
        self.chat_messages = []
        self.votes = {}
        self.display_lock = threading.RLock()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        with self.display_lock:
            print("\nDesconectado do servidor.")
        os._exit(0) # Força a saída de todas as threads
        
    def exposed_get_username(self):
        # O servidor chama isso no on_connect
        return self.username
     
    #trocar o ip do host para o ip do pc que esta sendo o servidor no radmin vpn
    def connect_to_server(self, host="26.254.252.239", port=18861):
        try:
            self.conn = rpyc.connect(host, port, service=self)
            self.game_service = self.conn.root
            
            self.thread = threading.Thread(target=self.conn.serve_threaded)
            self.thread.daemon = True
            self.thread.start()
            with self.display_lock:
                print(f"Conectado ao servidor como {self.username}")
            
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def update_game_state(self):
        """Busca o estado mais recente do jogo no servidor."""
        try:
            # Busca todos os dados de forma atômica
            current_page_id, current_page_json, chat_json, votes_json = self.game_service.exposed_get_atomic_game_state()

            self.current_page_id = current_page_id
            
            # Converte as strings JSON de volta para objetos Python
            self.current_page_data = json.loads(current_page_json)
            self.chat_messages = json.loads(chat_json)
            self.votes = json.loads(votes_json)
            
            # Redesenha a tela inteira
            self._print_full_game_state()
            
        except EOFError:
            pass 
        except Exception as e:
            with self.display_lock:
                print(f"\nErro ao atualizar estado: {e}")

    def _print_full_game_state(self):
        """Limpa o console e desenha a UI do jogo."""
        with self.display_lock:
            os.system("cls" if os.name == "nt" else "clear") 
            if not self.current_page_data:
                print("Conectando...")
                return

            print("=" * 50)
            print(f"Página Atual: {self.current_page_id}")
            print("=" * 50)
            print(self.current_page_data["text"])
            print("\nOpções:")
            if self.current_page_data["choices"]:
                for i, choice in enumerate(self.current_page_data["choices"]):
                    print(f"  {i + 1}. {choice['text']}")
            else:
                print("  Fim da história.")

            print("\n" + "-" * 50)
            print("Votos Atuais:")
            if self.votes:
                vote_counts = {}
                # Os votos vêm como { "usuario": "indice_str" }
                for voter, choice_idx_str in self.votes.items():
                    choice_idx = int(choice_idx_str) 
                    vote_counts[choice_idx] = vote_counts.get(choice_idx, 0) + 1
                
                choices_len = len(self.current_page_data["choices"])
                for choice_idx, count in vote_counts.items():
                    if 0 <= choice_idx < choices_len:
                        print(f"  Opção {choice_idx + 1}: {count} votos")
            else:
                print("  Nenhum voto ainda.")
            print("-" * 50)

            print("Chat:")
            for msg in self.chat_messages:
                print(f"  {msg}")
            print("=" * 50)

    # Callbacks do servidor (usados para notificações push)
    def exposed_on_page_update(self, page_id, page_json):
        """Chamado pelo servidor quando a página avança."""
        page_changed = (self.current_page_id != page_id)
        self.current_page_id = page_id
        self.current_page_data = json.loads(page_json) 
        
        if page_changed:
            with self.display_lock:
                print(f"\n[SISTEMA] A página mudou! Pressione Enter para atualizar a tela.")

    def exposed_on_chat_update(self, messages_json):
        """Chamado pelo servidor quando uma nova msg de chat chega."""
        new_messages = json.loads(messages_json)
        if len(new_messages) > len(self.chat_messages):
            with self.display_lock:
                print(f"\n[SISTEMA] Nova mensagem no chat. Pressione Enter para atualizar.")
        
        self.chat_messages = new_messages

    def exposed_on_vote_update(self, votes_json):
        """Chamado pelo servidor quando um novo voto é registrado."""
        new_votes = json.loads(votes_json)
        if new_votes != self.votes:
             with self.display_lock:
                print(f"\n[SISTEMA] Um voto foi registrado. Pressione Enter para atualizar.")
        
        self.votes = new_votes 

    def handle_input(self, user_input):
        """Processa os comandos digitados pelo usuário."""
        try:
            if user_input.lower().startswith("chat "):
                message = user_input[5:].strip()
                if message:
                    self.game_service.exposed_send_chat_message(self.username, message)
            
            elif user_input.lower() == "avancar":
                # A função do servidor agora retorna uma msg de status
                success, msg = self.game_service.exposed_check_and_advance_page(self.username)
                if not success:
                    with self.display_lock:
                        # Exibe a msg (ex: "Aguardando Winicius...")
                        print(f"\n[SISTEMA] {msg}") 
                        time.sleep(1.5) 

            elif user_input: # Ignora 'Enter' vazio
                try:
                    choice_index = int(user_input) - 1
                    if self.current_page_data and 0 <= choice_index < len(self.current_page_data["choices"]):
                        success, msg = self.game_service.exposed_vote(self.username, choice_index)
                        if not success:
                            with self.display_lock:
                                print(f"\n[SISTEMA] {msg}")
                                time.sleep(1.5)
                    else:
                        with self.display_lock:
                            print("\n[SISTEMA] Escolha inválida. Digite o número da opção.")
                            time.sleep(1.5)
                except ValueError:
                    with self.display_lock:
                        print(f"\n[SISTEMA] Comando inválido. Digite um número, 'chat <mensagem>' ou 'avancar'.")
                        time.sleep(1.5)
            
            # Se o input for vazio (só Enter), o loop vai rodar e atualizar a tela
        
        except EOFError:
            with self.display_lock:
                print("\nConexão com o servidor perdida.")
            os._exit(1)

    def input_loop(self):
        """Loop principal do jogo: Atualiza a tela, pede input, processa."""
        while True:
            try:
                # 1. ATUALIZA E REDESENHA O ESTADO ATUAL
                self.update_game_state()
                
                # 2. PEDE O INPUT
                user_input = input(f"{self.username}> ") 
                
                # 3. PROCESSA O INPUT
                self.handle_input(user_input)
            except (EOFError, KeyboardInterrupt):
                with self.display_lock:
                    print("\nSaindo...")
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 client.py <seu_nome_de_usuario>")
        sys.exit(1)

    username = sys.argv[1]
    client = StoryGameClient(username)
    if client.connect_to_server():
        client.input_loop()

        if client.conn and not client.conn.closed:
            client.conn.close()
