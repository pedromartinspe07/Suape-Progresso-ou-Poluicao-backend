import os

class Config:
    # A variável de ambiente DATABASE_URL será fornecida pelo Railway
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False