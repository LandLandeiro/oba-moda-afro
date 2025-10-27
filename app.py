# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from admin import init_admin
from flask_ckeditor import CKEditor
import math
import os
import datetime
# REMOVIDO: werkzeug.utils e slugify (o admin.py cuida disso)

# --- Configuração do Caminho do Banco de Dados ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'oba_afro.db')
upload_folder = os.path.join(basedir, 'static', 'uploads')
# REMOVIDO: ALLOWED_EXTENSIONS e allowed_file

def create_app():
    app = Flask(__name__)

    # --- Configurações do App ---
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte'
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
    app.config['FLASK_ADMIN_EXTRA_CSS'] = ['css/admin_custom.css']

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    db.init_app(app)
    CKEditor(app)
    init_admin(app) # <--- O Flask-Admin é inicializado aqui

    # Importa os models
    from models import (HeaderCategory, CircularCategory, Banner, Product, 
                        ProductSection, TextSection, FooterLink, Variation)

    # --- Context Processor ---
    @app.context_processor
    def inject_global_data():
        header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
        
        footer_links = {}
        if 'footer_link' in db.Model.metadata.tables:
             links = FooterLink.query.order_by(FooterLink.column, FooterLink.order).all()
             for link in links:
                 if link.column not in footer_links:
                     footer_links[link.column] = []
                 footer_links[link.column].append(link)
        
        return {
            'now': datetime.datetime.now(),
            'header_categories': header_categories,
            'footer_links': footer_links,
            'math': math
        }

    # --- Rotas Públicas (Permanecem) ---
    @app.route('/')
    def index():
        circular_categories_1 = CircularCategory.query.filter_by(section=1).order_by(CircularCategory.order).all()
        banners = Banner.query.order_by(Banner.order).all()
        product_sections = ProductSection.query.all()
        circular_categories_2 = CircularCategory.query.filter_by(section=2).order_by(CircularCategory.order).all()
        about_section = TextSection.query.filter_by(key='sobre-nos').first()

        return render_template(
            'index.html',
            circular_categories_1=circular_categories_1,
            banners=banners,
            product_sections=product_sections,
            circular_categories_2=circular_categories_2,
            about_section=about_section
        )

    @app.route('/produtos')
    def produtos():
        produtos_list = Product.query.filter_by(active=True).all()
        return render_template('produtos.html', produtos=produtos_list)

    @app.route('/produto/<slug>')
    def produto_detalhe(slug):
        produto = Product.query.filter_by(slug=slug, active=True).first_or_404()
        return render_template('produto_detalhe.html', produto=produto)

    @app.route('/carrinho')
    def carrinho():
        # Você precisará criar este template 'carrinho.html'
        # return render_template('carrinho.html') 
        return "Página do Carrinho (em construção)"

    @app.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
    def adicionar_carrinho(produto_id):
        variation_id = request.form.get('variation_id')
        quantity = request.form.get('quantity', 1)
        
        produto = Product.query.get_or_404(produto_id)
        
        if not variation_id:
             flash('Por favor, selecione um tamanho.', 'danger')
             return redirect(url_for('produto_detalhe', slug=produto.slug))

        variacao = Variation.query.get(variation_id)
        
        if not variacao or variacao.product_id != produto.id:
            flash('Variação inválida.', 'danger')
            return redirect(url_for('produto_detalhe', slug=produto.slug))
        
        # Aqui você adicionaria ao carrinho (ex: session)
        flash(f'Produto {produto.name} ({variacao.size}) adicionado ao carrinho!', 'success')
        return redirect(url_for('carrinho'))

    # --- ROTAS ADMINISTRATIVAS CUSTOMIZADAS (REMOVIDAS) ---
    # 
    # Todas as rotas como '/admin', '/admin/produtos', '/admin/produto/novo', etc.
    # foram REMOVIDAS daqui pois são controladas pelo 'init_admin(app)'
    # A função 'save_product_form' também foi removida.
    #
    
    return app

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Lembre-se de apagar o .db se você fez mudanças no models.py
        db.create_all()
    app.run(debug=True)