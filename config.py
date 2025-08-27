import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env em ambiente de desenvolvimento
# O Railway já gerencia isso em produção, então não precisamos dessa linha lá.
if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()

class Config:
    """Configurações de base para a aplicação Flask."""

    # A variável de ambiente DATABASE_URL é fornecida pelo Railway em produção,
    # e pelo arquivo .env em desenvolvimento.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Variáveis de ambiente para o MinIO
    MINIO_URL = os.environ.get('MINIO_URL')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
