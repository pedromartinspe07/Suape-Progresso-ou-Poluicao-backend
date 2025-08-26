import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Importa a classe de configuração
from config import Config

# Inicializa o Flask
app = Flask(__name__)
# Carrega as configurações do arquivo config.py
app.config.from_object(Config)

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# Permite requisições do seu frontend (ajuste para a URL do seu site em produção)
CORS(app)

# ====================================================================
# Models (Modelos de Dados)
# ====================================================================

class BlogPost(db.Model):
    __tablename__ = 'blog_post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    tags = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "category": self.category,
            "excerpt": self.excerpt,
            "image": self.image,
            "tags": self.tags.split(',') if self.tags else []
        }

# ====================================================================
# Rotas
# ====================================================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Retorna a lista de todos os posts do blog."""
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Retorna um único post com base no ID fornecido."""
    post = BlogPost.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@app.route('/api/posts', methods=['POST'])
def add_post():
    """Adiciona um novo post ao banco de dados."""
    data = request.json
    new_post = BlogPost(
        title=data['title'],
        date=data['date'],
        category=data['category'],
        excerpt=data['excerpt'],
        image=data.get('image'),
        tags=','.join(data.get('tags', [])) if 'tags' in data and data['tags'] else None
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API do blog está no ar!"})


# ====================================================================
# Ponto de entrada da aplicação
# ====================================================================

# O código dentro deste bloco só é executado quando você roda `python app.py`
# e é ignorado em ambientes de produção como o Railway, que usa o Gunicorn.
if __name__ == '__main__':
    # Cria as tabelas do banco de dados (se elas não existirem).
    # Isso é seguro para rodar e garante que a estrutura do banco esteja pronta.
    with app.app_context():
        db.create_all()

    # O servidor web de desenvolvimento Flask é usado apenas para testes locais.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)