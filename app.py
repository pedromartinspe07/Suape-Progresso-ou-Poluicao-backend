import os
import json
import redis 
from functools import wraps # Importa wraps para o decorador
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from minio import Minio
from werkzeug.utils import secure_filename

# Importa a classe de configuração
from config import Config

# Inicializa o Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# ====================================================================
# Configuração do Redis para Cache
# ====================================================================
redis_url = os.getenv('REDIS_URL')
if redis_url:
    cache = redis.from_url(redis_url, decode_responses=True)
else:
    cache = None
    print("WARNING: REDIS_URL not found. Cache disabled.")

# ====================================================================
# Configuração do MinIO para armazenamento de arquivos
# ====================================================================
minio_client = None
if os.getenv('MINIO_URL') and os.getenv('MINIO_ACCESS_KEY') and os.getenv('MINIO_SECRET_KEY'):
    try:
        minio_url = os.getenv('MINIO_URL')
        minio_access_key = os.getenv('MINIO_ACCESS_KEY')
        minio_secret_key = os.getenv('MINIO_SECRET_KEY')
        
        minio_client = Minio(
            minio_url,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=True
        )
        print("MinIO client initialized successfully.")
    except Exception as e:
        print(f"Error initializing MinIO client: {e}")
        minio_client = None
else:
    print("WARNING: MinIO variables not found. Image upload functionality disabled.")

# Inicializa as bibliotecas de segurança
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

CORS(app)

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário a partir do ID."""
    return User.query.get(int(user_id))

# ====================================================================
# Decoradores Personalizados
# ====================================================================

def admin_required(f):
    """
    Decora uma rota para que apenas usuários com o papel 'admin' possam acessá-la.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({"message": "Acesso não autorizado. Apenas administradores podem realizar esta ação."}), 403
        return f(*args, **kwargs)
    return decorated_function

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
    role = db.Column(db.String(10), default='editor')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
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
    """Retorna a lista de posts do blog, usando cache do Redis."""
    if cache:
        cached_posts = cache.get('all_posts')
        if cached_posts:
            return jsonify(json.loads(cached_posts))
    
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    posts_list = [post.to_dict() for post in posts]

    if cache:
        cache.set('all_posts', json.dumps(posts_list), ex=600)
    
    return jsonify(posts_list)

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Retorna um único post com base no ID fornecido."""
    post = BlogPost.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@app.route('/api/posts', methods=['POST'])
@login_required
def add_post():
    """Adiciona um novo post ao banco de dados."""
    data = request.json
    
    # Apenas usuários com a role 'admin' ou 'editor' podem adicionar posts.
    if current_user.role not in ['admin', 'editor']:
        return jsonify({"message": "Acesso não autorizado. Você não tem permissão para adicionar posts."}), 403

    image_url = None
    if 'image' in request.files and minio_client:
        image_file = request.files['image']
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            try:
                bucket_name = "blog-images"
                if not minio_client.bucket_exists(bucket_name):
                    minio_client.make_bucket(bucket_name)

                minio_client.put_object(
                    bucket_name,
                    filename,
                    image_file.stream,
                    length=image_file.content_length,
                    content_type=image_file.content_type
                )
                image_url = f"https://{os.getenv('MINIO_URL')}/{bucket_name}/{filename}"
            except Exception as e:
                print(f"Error uploading image to MinIO: {e}")

    new_post = BlogPost(
        title=data['title'],
        date=data['date'],
        category=data['category'],
        excerpt=data['excerpt'],
        image=image_url, 
        tags=','.join(data.get('tags', [])) if 'tags' in data and data['tags'] else None
    )
    db.session.add(new_post)
    db.session.commit()
    
    if cache:
        cache.delete('all_posts')

    return jsonify(new_post.to_dict()), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@admin_required # Apenas admins podem editar posts
def update_post(post_id):
    """Atualiza um post existente. O cache é invalidado após a atualização."""
    data = request.json
    post = BlogPost.query.get_or_404(post_id)

    # Atualiza os campos do post
    post.title = data.get('title', post.title)
    post.date = data.get('date', post.date)
    post.category = data.get('category', post.category)
    post.excerpt = data.get('excerpt', post.excerpt)
    post.tags = ','.join(data.get('tags', post.tags.split(','))) if data.get('tags') is not None else post.tags

    db.session.commit()
    
    # Invalida o cache
    if cache:
        cache.delete('all_posts')

    return jsonify({"message": "Post atualizado com sucesso!", "post": post.to_dict()})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@admin_required # Apenas admins podem deletar posts
def delete_post(post_id):
    """Deleta um post existente. O cache é invalidado após a exclusão."""
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    # Invalida o cache
    if cache:
        cache.delete('all_posts')

    return jsonify({"message": "Post excluído com sucesso!"}), 200

# ====================================================================
# Rotas de Autenticação
# ====================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Rota para registrar um novo usuário."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'editor') # Padrão para 'editor'

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
