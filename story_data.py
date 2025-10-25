story_pages = {
    "start": {
        "text": "Você acorda em uma floresta escura. Há dois caminhos à sua frente: um à esquerda, que parece levar a uma caverna, e um à direita, que segue por uma trilha iluminada pelo luar. O que você faz?",
        "emoji": "🌳",
        # Este link estava funcionando
        "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1170",
        "choices": [
            {"text": "Investigar a caverna à esquerda.", "emoji": "🦇", "next_page": "caverna"},
            {"text": "Seguir pela trilha iluminada à direita.", "emoji": "🌕", "next_page": "trilha"}
        ]
    },
    "caverna": {
        "text": "Você entra na caverna escura. O ar é frio e úmido. No fundo, você vê um brilho fraco. Parece ser uma tocha ou um olho. O que você faz?",
        "emoji": "🦇",
        # URL CORRIGIDO: Imagem de uma entrada de caverna escura
        "image_url": "https://media.istockphoto.com/id/1470878057/pt/foto/sunlight-through-the-cave-hole.webp?a=1&b=1&s=612x612&w=0&k=20&c=Rt9-PHVaSV8RU6nh1oqxET8W39PjPXUjDNypVp3n5Vg=",
        "choices": [
            {"text": "Aproximar-se do brilho.", "emoji": "👀", "next_page": "brilho_caverna"},
            {"text": "Voltar para a entrada da caverna.", "emoji": "🏃", "next_page": "start"}
        ]
    },
    "trilha": {
        "text": "Você segue pela trilha iluminada. O caminho é tranquilo e você ouve o canto de pássaros noturnos. Após alguns minutos, a trilha se divide em duas: uma que sobe uma colina e outra que desce para um vale. O que você faz?",
        "emoji": "🌕",
        # URL CORRIGIDO: Imagem de uma trilha que se divide
        "image_url": "https://images.unsplash.com/photo-1684929579439-2282e031732f?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1374",
        "choices": [
            {"text": "Subir a colina.", "emoji": "⛰️", "next_page": "colina"},
            {"text": "Descer para o vale.", "emoji": "🏞️", "next_page": "vale"}
        ]
    },
    "brilho_caverna": {
        "text": "Ao se aproximar, você percebe que o brilho vem de um par de olhos grandes e amarelos. Uma criatura enorme se levanta e ruge. Você não tem tempo para reagir. Fim de jogo.",
        "emoji": "👹",
        # URL CORRIGIDO: Imagem de olhos brilhantes no escuro
        "image_url": "https://elements-resized.envatousercontent.com/elements-video-cover-images/4cdf752d-f22b-4dc0-8cc0-15c082851949/video_preview/video_preview_0000.jpg?w=500&cf_fit=cover&q=85&format=auto&s=fff079d9c8d09ac7ac018a3551da6bced05f19160f10998b03e25da1a514f41a",
        "choices": []
    },
    "colina": {
        "text": "Você sobe a colina e encontra um acampamento abandonado. Há uma fogueira ainda acesa e alguns suprimentos. Você decide descansar e passar a noite. Fim de jogo.",
        "emoji": "🏕️",
        # URL CORRIGIDO: Imagem de um acampamento à noite
        "image_url": "https://images.unsplash.com/photo-1487730116645-74489c95b41b?auto=format&fit=crop&w=1170",
        "choices": []
    },
    "vale": {
        "text": "Você desce para o vale e encontra um rio. A água é cristalina e você vê peixes nadando. Você decide seguir o rio. Fim de jogo.",
        "emoji": "🏞️",
        # Este link parecia estar funcionando
        "image_url": "https://images.unsplash.com/photo-1478827387698-1527781a4887?auto=format&fit=crop&w=1170",
        "choices": []
    }
}

# --- Dados Iniciais do Jogo ---
# Não mexa neles
current_page_id = "start"
chat_messages = []
votes = {}