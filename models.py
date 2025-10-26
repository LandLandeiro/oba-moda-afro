from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)
    imagem = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class ConteudoSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo_principal = db.Column(db.String(200))
    subtitulo = db.Column(db.String(200))
    imagem_hero = db.Column(db.String(200))
    sobre_titulo = db.Column(db.String(200))
    sobre_texto = db.Column(db.Text)
    whatsapp = db.Column(db.String(20))
