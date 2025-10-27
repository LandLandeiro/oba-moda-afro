# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from extensions import db
from admin import init_admin
from flask_ckeditor import CKEditor
import math
import os
import datetime
from sqlalchemy import not_
from urllib.parse import quote_plus as url_escape 

WHATSAPP_NUMBER = '+5515997479931' 

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'oba_afro.db')
upload_folder = os.path.join(basedir, 'static', 'uploads')

def create_app():
    app = Flask(__name__)

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
    init_admin(app) 

    from models import (HeaderCategory, CircularCategory, Banner, Product, 
                        ProductSection, TextSection, Variation, # FooterLink removido
                        Category
                        )

    @app.context_processor
    def inject_global_data():
        header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
        
        # --- LÓGICA DO 'footer_links' REMOVIDA DAQUI ---
        
        cart = session.get('cart', {})
        cart_item_count = sum(cart.values()) 
        
        all_categories = Category.query.order_by(Category.name).all()
        
        return {
            'now': datetime.datetime.now(),
            'header_categories': header_categories,
            # 'footer_links': footer_links, <-- REMOVIDO
            'math': math,
            'cart_item_count': cart_item_count,
            'all_categories': all_categories 
        }

    # ... (O resto do app.py não muda) ...

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

    @app.route('/categoria/<slug>')
    def categoria_produtos(slug):
        category = Category.query.filter_by(slug=slug).first_or_404()
        produtos_list = [product for product in category.products if product.active]
        return render_template(
            'categoria_produtos.html', 
            produtos=produtos_list,
            category=category
        )

    @app.route('/produto/<slug>')
    def produto_detalhe(slug):
        produto = Product.query.filter_by(slug=slug, active=True).first_or_404()
        return render_template(
            'produto_detalhe.html', 
            produto=produto
        )

    @app.route('/carrinho')
    def carrinho():
        cart_session = session.get('cart', {})
        cart_items = []
        total_price = 0
        whatsapp_message_lines = ["Olá! Gostaria de fazer o seguinte pedido:\n"]
        
        for var_id_str, quantity in cart_session.items():
            variation = Variation.query.get(var_id_str)
            if variation:
                product = variation.product
                subtotal = product.price * quantity
                total_price += subtotal
                
                cart_items.append({
                    'product': product,
                    'variation': variation,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                
                whatsapp_message_lines.append(
                    f"- {quantity}x {product.name} (Tamanho: {variation.size}) - R$ {subtotal:.2f}"
                )

        whatsapp_message_lines.append(f"\n*Total: R$ {total_price:.2f}*")
        whatsapp_message = "\n".join(whatsapp_message_lines)
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={url_escape(whatsapp_message)}"
        
        return render_template(
            'carrinho.html', 
            cart_items=cart_items, 
            total_price=total_price,
            whatsapp_url=whatsapp_url
        )

    @app.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
    def adicionar_carrinho(produto_id):
        if 'cart' not in session:
            session['cart'] = {}
        variation_id = request.form.get('variation_id')
        produto = Product.query.get_or_404(produto_id)
        if not variation_id:
             flash('Por favor, selecione um tamanho.', 'danger')
             return redirect(url_for('produto_detalhe', slug=produto.slug))
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity < 1: quantity = 1
        except (ValueError, TypeError):
            quantity = 1
        variacao = Variation.query.get(variation_id)
        if not variacao or variacao.product_id != produto.id:
            flash('Variação inválida.', 'danger')
            return redirect(url_for('produto_detalhe', slug=produto.slug))
        var_id_str = str(variation_id)
        current_in_cart = session['cart'].get(var_id_str, 0)
        total_wanted = current_in_cart + quantity
        if total_wanted > variacao.stock:
            flash(f'Desculpe, temos apenas {variacao.stock} unidades de {produto.name} ({variacao.size}) em estoque.', 'danger')
        else:
            session['cart'][var_id_str] = total_wanted
            session.modified = True 
            flash(f'{quantity}x {produto.name} ({variacao.size}) adicionado ao carrinho!', 'success')
        return redirect(url_for('carrinho'))

    @app.route('/carrinho/atualizar', methods=['POST'])
    def atualizar_carrinho():
        if 'cart' not in session:
            return redirect(url_for('carrinho'))
        for var_id_str, new_quantity_str in request.form.items():
            if var_id_str in session['cart']:
                try:
                    new_quantity = int(new_quantity_str)
                    if new_quantity < 1: 
                        session['cart'].pop(var_id_str, None)
                        continue
                    variation = Variation.query.get(var_id_str)
                    if new_quantity > variation.stock:
                        flash(f'Estoque máximo para {variation.product.name} ({variation.size}) é {variation.stock}.', 'warning')
                        session['cart'][var_id_str] = variation.stock
                    else:
                        session['cart'][var_id_str] = new_quantity
                except (ValueError, TypeError):
                    pass 
        session.modified = True
        return redirect(url_for('carrinho'))

    @app.route('/carrinho/remover/<int:variation_id>')
    def remover_do_carrinho(variation_id):
        var_id_str = str(variation_id)
        if 'cart' in session and var_id_str in session['cart']:
            session['cart'].pop(var_id_str, None)
            session.modified = True
            flash('Item removido do carrinho.', 'success')
        return redirect(url_for('carrinho'))

    return app

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)