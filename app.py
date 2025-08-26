import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

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
    posts = BlogPost.query.all()
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
        tags=','.join(data.get('tags', []))
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API do blog está no ar!"})


if __name__ == '__main__':
    # Cria as tabelas do banco de dados antes de iniciar o app
    # Isso só precisa ser feito uma vez, ou a cada vez que a estrutura do Model for alterada.
    with app.app_context():
        db.create_all()

    # Em ambiente de produção no Railway, o servidor é executado de forma diferente
    # por isso, o `app.run` é usado apenas para testes locais.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)