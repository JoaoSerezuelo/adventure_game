import rpyc
import threading
import time
import json 
from story_data import story_pages, current_page_id, chat_messages, votes

class StoryGameService(rpyc.Service):
    def exposed_get_atomic_game_state(self):
        """Busca página, chat, votos e contagem de jogadores de forma atômica."""
        with self.lock:
            page_id = self.current_page_id
            page_data_json = json.dumps(story_pages[page_id])
            chat_json = json.dumps(list(self.chat_messages))
            votes_json = json.dumps(dict(self.votes))
            
            # NOVO: Adiciona contagem de jogadores
            current_players = len(self.client_map)
            total_players_ever = len(self.all_player_names)
            
            return page_id, page_data_json, chat_json, votes_json, current_players, total_players_ever
        

    def __init__(self):
        self.current_page_id = current_page_id
        self.chat_messages = chat_messages
        self.votes = votes
        self.lock = threading.Lock()
        self.clients = [] 
        self.client_map = {} # Mapeia 'conn.root' (serviço cliente) -> 'username'
        self.players_ready_to_advance = set()
        
        # NOVO: Rastreia todos os jogadores que já se conectaram
        self.all_player_names = set() 
        self.max_players_connected = 0 # Mantido, mas a lógica de avanço usará all_player_names

    def on_connect(self, conn):
        try:
            # o cliente expõe exposed_get_username — o RPyC permite chamar conn.root.get_username()
            username = conn.root.get_username() 
            if not username:
                raise ValueError("Cliente não retornou um username.")
            
            # NOVO: Adiciona o nome ao conjunto persistente
            with self.lock:
                self.all_player_names.add(username)
                
            self.client_map[conn.root] = username
            self.clients.append(conn)
            
            current_player_count = len(self.client_map)
            if current_player_count > self.max_players_connected:
                self.max_players_connected = current_player_count
                
            print(f"Cliente conectado: {conn} (Usuário: {username})")
            print(f"Jogadores atuais: {current_player_count}. Máximo de jogadores: {self.max_players_connected}")
            print(f"Lista de todos os jogadores que já entraram: {self.all_player_names}")


        except Exception as e:
            print(f"Falha na conexão do cliente: {e}")
            conn.close() 

    def on_disconnect(self, conn):
        print(f"Cliente desconectado: {conn}")
        if conn in self.clients:
            self.clients.remove(conn)
        
        username = self.client_map.pop(conn.root, None) 
        
        # Quando desconecta, removemos apenas o estado "pronto"
        if username and username in self.players_ready_to_advance:
            self.players_ready_to_advance.remove(username)
            print(f"Estado 'pronto' do usuário {username} removido.")
        
        # NÃO remover o voto do jogador — voto persiste mesmo se desconectar
        if username and username in self.votes:
            print(f"Usuário {username} desconectado. Seu voto foi mantido.")

    def exposed_get_current_page(self):
        with self.lock:
            page_data_json = json.dumps(story_pages[self.current_page_id])
            return self.current_page_id, page_data_json 

    def exposed_get_chat_messages(self):
        with self.lock:
            return json.dumps(list(self.chat_messages)) 

    def exposed_get_votes(self):
        with self.lock:
            return json.dumps(dict(self.votes)) 

    def exposed_send_chat_message(self, username, message):
        chat_json = None 
        with self.lock:
            self.chat_messages.append(f"[{username}] {message}")
            chat_json = json.dumps(list(self.chat_messages)) 
        
        self._notify_clients_chat_update(chat_json) 
        return True

    def exposed_vote(self, username, choice_index):
        votes_json = None 
        with self.lock:
            current_page = story_pages[self.current_page_id]
            if not (0 <= choice_index < len(current_page['choices'])):
                return False, "Escolha inválida."

            self.votes[username] = choice_index
            
            # Se o usuário votar, seu estado de "pronto" é resetado
            if username in self.players_ready_to_advance:
                self.players_ready_to_advance.remove(username)
                
            votes_json = json.dumps(dict(self.votes)) 
        
        self._notify_clients_vote_update(votes_json) 
        return True, "Voto registrado."

    def exposed_check_and_advance_page(self, username):
        page_json = None
        id_copy = None
        chat_json = None
        votes_json = None
        advanced = False

        with self.lock:
            current_page_data = story_pages[self.current_page_id]
            if not current_page_data['choices']:
                return False, "Página final, sem escolhas."

            # --- LÓGICA DE AVANÇO (USANDO all_player_names) ---
            
            # Usa o conjunto de todos os jogadores que já se conectaram
            all_players = set(self.all_player_names)  # faz cópia defensiva
            total_players_required = len(all_players)
            
            if total_players_required == 0:
                return False, "Nenhum jogador conectado."
            
            # 1. Marca o jogador como "pronto"
            self.players_ready_to_advance.add(username)
            print(f"Jogador {username} está pronto. Prontos: {self.players_ready_to_advance}")

            # 2. Verifica se todos votaram (considerando todos que já entraram)
            voted_players = set(self.votes.keys())
            waiting_for_vote = sorted(list(all_players - voted_players))
            
            if waiting_for_vote:
                # Se ainda faltam votos, o clique em "Avançar" não conta — remove o "pronto" deste usuário
                self.players_ready_to_advance.discard(username)
                msg = f"Aguardando {len(waiting_for_vote)}/{total_players_required} votarem: {', '.join(waiting_for_vote)}"
                return False, msg

            # 3. Se todos votaram, verifica se todos estão prontos (clicaram "Avançar")
            ready_players = set(self.players_ready_to_advance)
            waiting_for_ready = sorted(list(all_players - ready_players))

            if waiting_for_ready:
                msg = f"Aguardando {len(waiting_for_ready)}/{total_players_required} clicarem 'Avançar': {', '.join(waiting_for_ready)}"
                return False, msg

            # 4. Se todos votaram E todos estão prontos, processa os votos
            vote_counts = {}
            for voter, choice_idx in self.votes.items():
                vote_counts[choice_idx] = vote_counts.get(choice_idx, 0) + 1
            
            if not vote_counts:
                 # Caso excepcional: limpa estado de pronto e recusa avanço
                 self.players_ready_to_advance.clear()
                 return False, "Sem votos válidos."

            max_votes = max(vote_counts.values())
            winners = []
            for choice_idx, count in vote_counts.items():
                if count == max_votes:
                    winners.append(choice_idx)
            
            if len(winners) > 1:
                # Lógica de empate: anuncia no chat, reseta votos e estado "pronto" e notifica os clientes
                self.chat_messages.append(f"[SISTEMA] Houve um empate! Votem novamente para desempatar.")
                chat_json_tie = json.dumps(list(self.chat_messages))
                threading.Timer(0.1, self._notify_clients_chat_update, [chat_json_tie]).start()
                
                # Reseta votos e estado de pronto para a nova votação
                self.players_ready_to_advance.clear()
                self.votes.clear() 
                
                # Notifica os clientes que os votos foram zerados
                votes_json_tie = json.dumps(self.votes)
                threading.Timer(0.1, self._notify_clients_vote_update, [votes_json_tie]).start()
                
                return False, "Empate na votação. Votem novamente!"

            winning_choice_index = winners[0]

            if winning_choice_index != -1:
                if 0 <= winning_choice_index < len(current_page_data['choices']):
                    next_page_id = current_page_data['choices'][winning_choice_index]['next_page']
                    self.current_page_id = next_page_id
                    page_copy = story_pages[self.current_page_id] 
                    
                    # Limpa tudo para a nova página (votos persistentes já foram processados)
                    self.votes.clear() 
                    self.players_ready_to_advance.clear() 
                    
                    self.chat_messages.append(f"[SISTEMA] A maioria votou em: '{current_page_data['choices'][winning_choice_index]['text']}'. Avançando.")
                    
                    id_copy = self.current_page_id
                    page_json = json.dumps(page_copy)
                    chat_json = json.dumps(list(self.chat_messages))
                    votes_json = json.dumps(dict(self.votes))
                    advanced = True
                else:
                    return False, "Erro: Voto vencedor inválido."
            else:
                return False, "Não foi possível determinar um vencedor."
            
            # --- FIM DA LÓGICA DE AVANÇO ---

        # Fora do lock: notifica clientes se avançou
        if advanced:
            self._notify_clients_page_update(id_copy, page_json)
            self._notify_clients_chat_update(chat_json)
            self._notify_clients_vote_update(votes_json)
            return True, f"Avançado para a página: {id_copy}"
            
        return False, "Não foi possível avançar a página."
    
    # Funções de notificação (sem alterações)
    def _notify_clients_page_update(self, page_id, page_json):
        for client_conn in self.clients:
            try:
                if hasattr(client_conn.root, 'on_page_update'):
                    client_conn.root.on_page_update(page_id, page_json)
            except Exception as e:
                print(f"Erro ao notificar cliente (página): {e}")

    def _notify_clients_chat_update(self, chat_json):
        for client_conn in self.clients:
            try:
                if hasattr(client_conn.root, 'on_chat_update'):
                    client_conn.root.on_chat_update(chat_json)
            except Exception as e:
                print(f"Erro ao notificar cliente (chat): {e}")

    def _notify_clients_vote_update(self, votes_json):
        for client_conn in self.clients:
            try:
                if hasattr(client_conn.root, 'on_vote_update'):
                    client_conn.root.on_vote_update(votes_json)
            except Exception as e:
                print(f"Erro ao notificar cliente (voto): {e}")


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    print("Iniciando servidor RPyC...")
    t = ThreadedServer(StoryGameService(), hostname="0.0.0.0", port=18861)
    t.start()
