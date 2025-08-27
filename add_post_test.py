import requests
import json

# URL da sua API local ou de produção.
# Certifique-se de que o backend está rodando e a URL está correta.
# Esta URL é um exemplo para o seu backend no Railway.
API_URL = "https://suape-progresso-ou-poluicao-backend-production.up.railway.app/api/posts"

# Um token de autenticação de exemplo.
# Em um cenário real, você obteria este token após fazer login.
# Aqui, estamos assumindo que a rota add_post precisa de login.
# Lembre-se de substituir este token por um real, se necessário.
AUTH_TOKEN = "SEU_TOKEN_DE_AUTENTICACAO_AQUI" 

# Headers para a requisição, incluindo o token de autenticação
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}" # Exemplo de como enviar um token de autenticação
}

# ====================================================================
# Lista de posts com informações mais detalhadas
# ====================================================================

posts_cientificos = [
    {
        "title": "Impactos Ambientais da Indústria de Suape: Uma Análise da Qualidade da Água",
        "date": "26 de Agosto, 2025",
        "category": "pesquisa",
        "excerpt": (
            "Este estudo científico examina as alterações físico-químicas e biológicas nos ecossistemas aquáticos "
            "do Complexo de Suape. Os resultados indicam a presença de poluentes orgânicos e inorgânicos em níveis "
            "elevados, correlacionados com a atividade portuária e industrial, levantando preocupações sobre a "
            "saúde dos manguezais e a biodiversidade marinha local. As amostras foram coletadas em pontos "
            "estratégicos ao longo dos estuários e lagos de água doce, utilizando métodos espectrométricos e de "
            "cromatografia de gás, confirmando a necessidade de monitoramento contínuo e medidas de mitigação "
            "mais rigorosas para assegurar a sustentabilidade ambiental da região a longo prazo."
        ),
        "author": "Dr. Ana Rodrigues",
        "image": "/assets/images/analise-agua.jpg",
        "tags": ["Meio Ambiente", "Poluição", "Qualidade da Água", "Pesquisa"]
    },
    {
        "title": "Desenvolvimento Socioeconômico vs. Proteção Ambiental: O Dilema de Suape",
        "date": "20 de Agosto, 2025",
        "category": "artigo",
        "excerpt": (
            "A expansão industrial em Suape trouxe crescimento econômico e empregos, mas também gerou tensões com "
            "comunidades tradicionais e ecossistemas sensíveis. Este artigo analisa as políticas públicas e o impacto "
            "social das grandes obras, destacando a importância de um modelo de desenvolvimento que integre as "
            "dimensões econômica, social e ambiental. Entrevistas com líderes comunitários e dados sobre o deslocamento "
            "populacional revelam que o progresso econômico não se traduziu em melhoria equitativa para todos, "
            "especialmente para os pescadores e agricultores locais, cujos meios de subsistência foram diretamente afetados."
        ),
        "author": "Prof. João Silva",
        "image": "/assets/images/desenvolvimento-social.jpg",
        "tags": ["Economia", "Desenvolvimento", "Impacto Social", "Sustentabilidade"]
    },
    {
        "title": "Estratégias de Mitigação de Efeitos Ambientais em Portos Industriais",
        "date": "10 de Agosto, 2025",
        "category": "relatorio",
        "excerpt": (
            "Este relatório técnico propõe um conjunto de medidas para minimizar os impactos ambientais no Complexo de Suape. "
            "As estratégias incluem a implementação de tecnologias de tratamento de efluentes, o aumento do uso de energias "
            "renováveis, e a criação de zonas de proteção ambiental estritas. O documento também sugere a colaboração "
            "entre o setor público, empresas privadas e a sociedade civil para monitorar e auditar as práticas ambientais. "
            "A adoção de indicadores de performance ambiental (KPIs) é recomendada como uma ferramenta essencial para "
            "avaliar o sucesso das políticas e garantir a conformidade com as normas internacionais de proteção ambiental."
        ),
        "author": "Equipe de Consultoria Ambiental",
        "image": "/assets/images/relatorio-ambiental.jpg",
        "tags": ["Relatório", "Mitigação", "Tecnologia", "Política Ambiental"]
    }
]

# ====================================================================
# Função para enviar os posts
# ====================================================================

def send_posts_to_api():
    """Envia cada post da lista para a API e exibe o resultado."""
    print("Iniciando o envio de posts de teste para a API...")
    for i, post in enumerate(posts_cientificos):
        print(f"\n--- Enviando Post {i + 1}: '{post['title']}' ---")
        try:
            # Envia a requisição POST com os dados em formato JSON
            response = requests.post(API_URL, json=post, headers=headers)
            
            # Verifica se a requisição foi bem-sucedida (código 201 Created)
            if response.status_code == 201:
                print("Post adicionado com sucesso!")
                print("Resposta da API:", json.dumps(response.json(), indent=4))
            else:
                print(f"Erro ao adicionar o post. Código de status: {response.status_code}")
                print("Mensagem de erro:", response.text)

        except requests.exceptions.ConnectionError as e:
            print("Erro de conexão. Certifique-se de que o seu servidor Flask está rodando.")
            print(e)
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    send_posts_to_api()
