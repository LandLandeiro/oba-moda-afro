# app.py
from flask import Flask, render_template
from extensions import db
from admin import init_admin
from flask_ckeditor import CKEditor
import math
import os
import datetime

# --- Configuração do Caminho do Banco de Dados ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'oba_afro.db')
upload_folder = os.path.join(basedir, 'static', 'uploads')

def create_app():
    app = Flask(__name__)

    # --- Configurações do App ---
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte'
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['FLASK_ADMIN_SWATCH'] = 'flatly' # Mantém um tema base

    # --- ADICIONA O CSS CUSTOMIZADO ---
    # O caminho é relativo à pasta 'static'
    app.config['FLASK_ADMIN_EXTRA_CSS'] = ['css/admin_custom.css']

    # Conecta o db ao app
    db.init_app(app)

    # babel.init_app(app) # Mantenha comentado ou remova

    # --- INICIALIZE OUTROS PLUGINS ---
    CKEditor(app)
    init_admin(app)

    # Importa os models
    from models import HeaderCategory, CircularCategory, Banner, Product, ProductSection, TextSection, FooterLink

    # --- Context Processor ---
    @app.context_processor
    def inject_current_date():
        return {'now': datetime.datetime.now()}

    # --- Registro das Rotas ---
    @app.route('/')
    def index():
        # ... (código da rota index não muda) ...
        header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
        circular_categories_1 = CircularCategory.query.filter_by(section=1).order_by(CircularCategory.order).all()
        banners = Banner.query.order_by(Banner.order).all()
        product_sections = ProductSection.query.all()
        circular_categories_2 = CircularCategory.query.filter_by(section=2).order_by(CircularCategory.order).all()
        about_section = TextSection.query.filter_by(key='sobre-nos').first()
        footer_links = {}
        
        # Consulta FooterLink apenas se o modelo ainda existir
        if 'FooterLink' in db.Model.metadata.tables: # Verifica se a tabela existe
             links = FooterLink.query.order_by(FooterLink.column, FooterLink.order).all()
             for link in links:
                 if link.column not in footer_links:
                     footer_links[link.column] = []
                 footer_links[link.column].append(link)
        
        # Se FooterLink foi removido, passa um dicionário vazio
        else:
            footer_links = {}


        return render_template(
            'index.html',
            header_categories=header_categories,
            circular_categories_1=circular_categories_1,
            banners=banners,
            product_sections=product_sections,
            circular_categories_2=circular_categories_2,
            about_section=about_section,
            footer_links=footer_links, # Passa mesmo que esteja vazio
            math=math
        )

    return app


# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)