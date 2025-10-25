import streamlit as st
import rpyc
import json
import time
from streamlit_autorefresh import st_autorefresh

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Aventura Cooperativa")

# --- Definição do Serviço Cliente RPyC ---
class ClientHandshakeService(rpyc.Service):
    """
    Serviço RPyC mínimo que o cliente Streamlit expõe ao servidor.
    Sua única função real é responder ao 'exposed_get_username'
    para que o servidor possa registrar o jogador.
    """
    def __init__(self, username):
        self._username = username

    def exposed_get_username(self):
        """O servidor chama isso imediatamente após a conexão."""
        return self._username

    def exposed_on_page_update(self, page_id, page_json):
        """Ignorado, pois estamos usando polling (st_autorefresh)"""
        pass

    def exposed_on_chat_update(self, messages_json):
        """Ignorado, pois estamos usando polling"""
        pass

    def exposed_on_vote_update(self, votes_json):
        """Ignorado, pois estamos usando polling"""
        pass

# --- Funções de Callback dos Botões (Handlers) ---

def handle_vote(choice_index):
    """Chamado quando um botão de voto (escolha) é clicado."""
    try:
        username = st.session_state.username
        game_service = st.session_state.game_service
        
        success, msg = game_service.exposed_vote(username, choice_index)
        
        if success:
            st.toast("Voto registrado!", icon="🗳️")
        else:
            st.toast(msg, icon="⚠️") 
    except Exception as e:
        st.error(f"Erro ao votar: {e}")
        handle_disconnect() 

# --- FUNÇÃO DE CHAT ---
def handle_chat_send():
    """Chamado quando o botão 'Enviar' do chat é clicado ou Enter é pressionado."""
    message = st.session_state.chat_input_text
    if message: 
        try:
            username = st.session_state.username
            game_service = st.session_state.game_service
            game_service.exposed_send_chat_message(username, message)
            # Limpa a caixa de texto após o envio
            st.session_state.chat_input_text = "" 
        except Exception as e:
            st.error(f"Erro ao enviar mensagem: {e}")
            handle_disconnect()

# --- FUNÇÃO DE AVANÇAR ---
def handle_advance_page():
    """Chamado quando o botão 'Tentar Avançar' é clicado."""
    try:
        game_service = st.session_state.game_service
        username = st.session_state.username # Pega o nome do usuário
        
        # Envia o 'username' para o servidor
        # O 'msg' de retorno será "Aguardando Winicius...", etc.
        success, msg = game_service.exposed_check_and_advance_page(username)
        
        if success:
            st.toast("Avançando para a próxima página!", icon="🚀")
        else:
            # Mostra a mensagem do servidor (ex: "Aguardando todos votarem")
            st.toast(msg, icon="ℹ️")
    except Exception as e:
        st.error(f"Erro ao avançar a página: {e}")
        handle_disconnect()

# --- FUNÇÃO DE DESCONECTAR ---
def handle_disconnect():
    """
    Limpa o estado da sessão em caso de erro grave (ex: servidor caiu).
    Isso força o usuário a voltar para a tela de login.
    """
    st.error("Conexão perdida com o servidor. A página será recarregada.")
    
    # Tenta fechar a conexão RPyC se ela existir
    if 'rpyc_conn' in st.session_state and st.session_state.rpyc_conn:
        try:
            st.session_state.rpyc_conn.close()
        except:
            pass # Ignora erros ao fechar
    
    # Limpa todo o estado da sessão para forçar o login
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    time.sleep(2) 
    st.rerun() # Recarrega a página

# --- Função Principal da Aplicação ---

def run_app():
    """
    Executa a lógica principal da aplicação Streamlit.
    """

    # --- 1. Inicialização do Estado da Sessão ---
    # Garante que as chaves existam no início
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'rpyc_conn' not in st.session_state:
        st.session_state.rpyc_conn = None
    if 'game_service' not in st.session_state:
        st.session_state.game_service = None
    if 'client_service' not in st.session_state:
        st.session_state.client_service = None

    # --- 2. Tela de Login ---
    # Se o usuário não estiver logado, mostra a tela de login.
    if st.session_state.username is None:
        st.title("Aventura Cooperativa - Login")
        
        st.image(
            # Link da imagem de login (pode ser trocado)
            "https://cms-assets.unrealengine.com/AiKUh5PQCTaOFnmJDZJBfz/resize=width:1920/output=format:webp/cm7ak1ock3lsi06mver24fr7p", 
            caption="Bem-vindo à Aventura Cooperativa!", 
            use_container_width=True
        )
        
        username_input = st.text_input("Digite seu nome de usuário:", key="login_username")
        
        if st.button("Entrar no Jogo ⚔️", key="login_button"):
            if username_input:
                st.session_state.username = username_input 
                st.rerun() # Recarrega a página para ir para a tela de conexão
            else:
                st.error("Por favor, digite um nome de usuário.")
        return # Para a execução aqui se não estiver logado

    # --- 3. Estabelecimento da Conexão RPyC ---
    # Se o usuário estiver logado, mas ainda não conectado ao RPyC
    if st.session_state.rpyc_conn is None:
        username = st.session_state.username
        # Cria o serviço de handshake que o servidor chamará
        st.session_state.client_service = ClientHandshakeService(username)
        
        try:
            with st.spinner(f"Conectando ao servidor como {username}..."):
                conn = rpyc.connect(
                    "localhost", 
                    18861, 
                    service=st.session_state.client_service
                )
                
                # Armazena a conexão e o serviço principal no estado da sessão
                st.session_state.rpyc_conn = conn
                st.session_state.game_service = conn.root 
                st.success("Conectado com sucesso!")
                time.sleep(1) 
                st.rerun() # Recarrega para entrar no loop do jogo
        except Exception as e:
            st.error(f"Não foi possível conectar ao servidor: {e}")
            st.warning("Verifique se o 'server.py' está em execução.")
            st.session_state.username = None # Reseta o login
            if st.button("Tentar Novamente"):
                st.rerun() 
        return # Para a execução aqui se não estiver conectado

    # --- 4. Loop Principal do Jogo (LAYOUT LADO A LADO) ---
    
    # Atualiza a página a cada 3 segundos para buscar novos dados
    st_autorefresh(interval=1500, limit=None, key="game_refresher")

    try:
        # Pega os serviços do estado da sessão
        game_service = st.session_state.game_service
        username = st.session_state.username

        # --- Busca de Dados (Polling) ATÔMICO ---
        current_page_id, page_json, chat_json, votes_json, current_players, total_players_ever = game_service.exposed_get_atomic_game_state()

        # --- Deserialização dos Dados ---
        page_data = json.loads(page_json)
        chat_messages = json.loads(chat_json) 
        votes = json.loads(votes_json) 

        # --- Renderização da UI (SEM SIDEBAR) ---
        
        st.caption(f"Logado como: **{username}** 👋")
        st.caption(f"Jogadores conectados: **{current_players}** | Total na sessão (para avançar): **{total_players_ever}**")
        
        # Cria uma coluna central para o conteúdo principal
        _left, main_col, _right = st.columns([1, 2, 1]) 

        with main_col:
            
            page_emoji = page_data.get('emoji', '📜')
            st.title(f"{page_emoji} Página: {current_page_id}")
            
            # Mostra a imagem da história
            if page_data.get('image_url'):
                st.image(page_data['image_url'], caption="A cena atual", use_container_width=True)
            
            # Mostra o texto da história
            st.info(page_data["text"], icon=page_emoji)
            
            st.divider()
            
            # --- SEÇÃO LADO A LADO: VOTOS E CHAT ---
            col_votos, col_chat = st.columns(2) 

            with col_votos:
                # --- Seção de Votos ---
                st.header("🗳️ Votos Atuais") 
                if page_data["choices"]:
                    # Calcula a contagem de votos
                    vote_counts = {} 
                    for user, choice_idx in votes.items():
                        choice_idx_int = int(choice_idx) 
                        vote_counts[choice_idx_int] = vote_counts.get(choice_idx_int, 0) + 1
                    
                    for i, choice in enumerate(page_data["choices"]):
                        count = vote_counts.get(i, 0)
                        voters = [user for user, idx in votes.items() if int(idx) == i]
                        
                        # Chave dinâmica baseada na presença de eleitores
                        container_key = f"vote_display_{i}_voters_{bool(voters)}"
                        
                        # Criar um container para CADA opção de voto
                        vote_container = st.container(key=container_key)
                        
                        with vote_container:
                            choice_emoji = choice.get('emoji', '👉') 
                            st.markdown(f"**{choice_emoji} Opção {i+1}**: {count} voto(s)")
                            
                            if voters:
                                st.caption(f"Votos: {', '.join(voters)}")
                            
                            st.write("") # Adiciona um espaço
                        
                else:
                    st.write("A história terminou. Não há mais votos.")

            with col_chat:
                # --- Seção de Chat ---
                st.header("💬 Chat da Equipe")
                # Contêiner de chat com altura fixa
                chat_container = st.container(height=300)
                with chat_container:
                    for msg in chat_messages:
                        chat_container.text(msg)
                
                # Input e botão na vertical
                st.text_input(
                    "Sua mensagem:", 
                    label_visibility="collapsed", 
                    placeholder="Digite sua mensagem...",
                    key="chat_input_text"
                )
                st.button(
                    "Enviar ✉️", 
                    on_click=handle_chat_send, 
                    key="chat_send_btn",
                    use_container_width=True 
                )
            
            st.divider()
            # --- FIM DA SEÇÃO LADO A LADO ---


            # --- Seção de Ações (Escolhas) ---
            if page_data["choices"]:
                st.header("Faça sua escolha:")
                
                # Botões de escolha (layout vertical)
                for i, choice in enumerate(page_data["choices"]):
                    my_vote = votes.get(username)
                    my_vote_int = int(my_vote) if my_vote is not None else None 
                    
                    # Destaca o botão que o usuário votou
                    btn_type = "primary" if my_vote_int == i else "secondary"
                    
                    choice_emoji = choice.get('emoji', '👉')
                    button_text = f"{choice_emoji} {i+1}. {choice['text']}"
                    
                    st.button(
                        button_text, 
                        key=f"choice_{i}_{btn_type}",
                        on_click=handle_vote, 
                        args=(i,), 
                        use_container_width=True, 
                        type=btn_type 
                    )
                
                st.divider()
                
                # Botão de Avançar
                st.button(
                    "Tentar Avançar a Página 🚀", 
                    on_click=handle_advance_page,
                    key="advance_btn",
                    use_container_width=True, 
                    type="primary" 
                )
            
            else:
                # Se não houver escolhas, é o fim do jogo
                st.header("Fim da História 🎉") 
                st.success("Obrigado por jogar!")
                if st.button("Jogar Novamente 🔄"): 
                    st.warning("Para jogar novamente, o servidor ('server.py') precisa ser reiniciado manualmente.")


    except Exception as e:
        # Lida com erros de conexão ou outros problemas
        if "colocadas dentro de outras colunas" in str(e):
             st.error(f"Erro de Layout: {e}")
        elif "missing 1 required positional argument: 'username'" in str(e):
            st.error("Erro de Sincronia: O app está dessincronizado com o servidor. Recarregando...")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"Erro de conexão: {e}")
            handle_disconnect() 

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    run_app()
