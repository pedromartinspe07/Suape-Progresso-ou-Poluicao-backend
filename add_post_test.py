import requests
import json

# URL da sua API local. Certifique-se de que o backend está rodando!
API_URL = "https://suape-progresso-ou-poluicao-backend-production.up.railway.app/api/posts"

# Dados do post de teste que você quer enviar
test_post = {
    "title": "A Inovação Sustentável em Suape: Um Olhar para o Futuro",
    "date": "26 de Agosto, 2025",
    "category": "noticias",
    "excerpt": "Um novo projeto de energia renovável promete transformar a cadeia produtiva no Complexo Industrial e Portuário de Suape...",
    "image": "/assets/images/noticia-suape.jpg",
    "tags": ["Sustentabilidade", "Inovação", "Energia Limpa"]
}

try:
    # Envia a requisição POST com os dados em formato JSON
    response = requests.post(API_URL, json=test_post)
    
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