import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

# Importa a classe de configuração
from config import Config

# Inicializa o Flask
app = Flask(__name__)
# Carrega as configurações do arquivo config.py
app.config.from_object(Config)

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# Inicializa as bibliotecas de segurança
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Define a rota para o login

# Permite requisições do seu frontend (ajuste para a URL do seu site em produção)
CORS(app)

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário a partir do ID."""
    return User.query.get(int(user_id))

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

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='editor') # 'admin' ou 'editor'

    def set_password(self, password):
        """Criptografa a senha e armazena o hash."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
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
@login_required # Agora a rota só aceita requisições de usuários logados
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

# ====================================================================
# Rotas de Autenticação
# ====================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Rota para registrar um novo usuário."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'editor')

    if not username or not password:
        return jsonify({"message": "Username e senha são obrigatórios."}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Este usuário já existe."}), 409

    new_user = User(username=username, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!", "user": new_user.to_dict()}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Rota para o login de um usuário."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login bem-sucedido!", "user": user.to_dict()}), 200
    
    return jsonify({"message": "Usuário ou senha inválidos."}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Rota para fazer logout."""
    logout_user()
    return jsonify({"message": "Logout bem-sucedido!"}), 200

@app.route('/api/user', methods=['GET'])
@login_required
def get_current_user():
    """Retorna as informações do usuário logado."""
    return jsonify({"user": current_user.to_dict()})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API do blog está no ar!"})


# ====================================================================
# Ponto de entrada da aplicação
# ====================================================================

# O código dentro deste bloco só é executado quando você roda `python app.py`
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)