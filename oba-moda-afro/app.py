# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from extensions import db, login_manager, bcrypt, migrate # migrate foi importado
from admin import init_admin
from flask_ckeditor import CKEditor
import math
import os
import datetime
from sqlalchemy import not_
from urllib.parse import quote_plus as url_escape 
from flask_login import login_user, logout_user, current_user

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
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    app.config['FLASK_ADMIN_EXTRA_CSS'] = ['css/admin_custom.css']

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db) # migrate foi inicializado
    CKEditor(app)
    init_admin(app) 

    from models import (HeaderCategory, CircularCategory, Banner, Product, 
                        ProductSection, TextSection, Variation,
                        Category,
                        User,
                        FooterLink, # <-- 1. IMPORTAR FooterLink
                        Order, SiteStat,
                        OrderItem
                        )
    
    @login_manager.user_loader
    def load_user(user_id):
        """Função que o Flask-Login usa para recarregar o usuário da sessão."""
        return User.query.get(int(user_id))

    # --- ATUALIZADO: CONTEXT PROCESSOR ---
    @app.context_processor
    def inject_global_data():
        header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
        
        cart = session.get('cart', {})
        cart_item_count = sum(cart.values()) 
        
        all_categories = Category.query.order_by(Category.name).all()
        
        # --- 2. NOVA LÓGICA DO RODAPÉ ---
        # Busca todos os links e os agrupa por coluna em um dicionário
        footer_links_db = FooterLink.query.order_by(FooterLink.column, FooterLink.order).all()
        footer_links_grouped = {}
        for link in footer_links_db:
            if link.column not in footer_links_grouped:
                footer_links_grouped[link.column] = []
            footer_links_grouped[link.column].append(link)
        # --- FIM DA LÓGICA DO RODAPÉ ---

        return {
            'now': datetime.datetime.now(),
            'header_categories': header_categories,
            'math': math,
            'cart_item_count': cart_item_count,
            'all_categories': all_categories, 
            'current_user': current_user,
            'footer_links': footer_links_grouped # <-- 3. ENVIA PARA O TEMPLATE
        }

    def get_stat(key):
        """Busca ou cria uma estatística e retorna o objeto."""
        stat = SiteStat.query.filter_by(key=key).first()
        if not stat:
            stat = SiteStat(key=key, value=0)
            db.session.add(stat)
            # Tenta salvar imediatamente
            try:
                db.session.commit()
            except:
                db.session.rollback()
                stat = SiteStat.query.filter_by(key=key).first()
        return stat
    
    # --- Rotas da Loja ---

    @app.route('/')
    def index():
        try:
            stat = get_stat('total_visitas')
            stat.value += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao contar visita: {e}")
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
        
        # --- RASTREAMENTO DE VISUALIZAÇÃO DE PRODUTO ---
        try:
            produto.view_count += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao contar view do produto: {e}")
        # --- FIM DO RASTREAMENTO ---

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
                # Preço correto (com promoção)
                subtotal = product.current_price * quantity
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
        
        session['whatsapp_message'] = "\n".join(whatsapp_message_lines)
        
        return render_template(
            'carrinho.html', 
            cart_items=cart_items, 
            total_price=total_price
        )
    
    # --- ROTA DE CHECKOUT (CRIAR PEDIDO) ATUALIZADA ---
    @app.route('/checkout/criar-pedido', methods=['POST'])
    def criar_pedido():
        """
        Esta rota é chamada quando o usuário clica em "Finalizar Pedido".
        1. Valida o estoque (previne race condition)
        2. Subtrai o estoque
        3. Cria o Pedido (Lead) e os OrderItems no banco
        4. Redireciona ao WhatsApp.
        """
        cart_session = session.get('cart', {})
        whatsapp_message = session.get('whatsapp_message', 'Erro: Carrinho vazio.')
        
        if not cart_session:
            flash('Seu carrinho está vazio.', 'warning')
            return redirect(url_for('carrinho'))

        # --- 1. PASSO DE VALIDAÇÃO (Checa estoque ANTES de subtrair) ---
        for var_id_str, quantity in cart_session.items():
            variation = Variation.query.get(var_id_str)
            if not variation or variation.stock < quantity:
                # Se alguém comprou o item enquanto ele estava no carrinho
                flash(f'Desculpe, o item {variation.product.name} ({variation.size}) não tem mais {quantity} unidades em estoque. Por favor, ajuste seu carrinho.', 'danger')
                return redirect(url_for('carrinho'))

        # Se a validação passou, o estoque está garantido.

        # --- 2. PASSO DE PROCESSAMENTO (Subtrai o estoque e cria o pedido) ---
        try:
            total_price = 0
            
            # Cria o Pedido (ainda sem preço total)
            novo_pedido = Order(total_price=0, status='Pendente')
            db.session.add(novo_pedido)
            
            items_for_message = [] # Para a msg do WhatsApp

            for var_id_str, quantity in cart_session.items():
                variation = Variation.query.get(var_id_str)
                
                # Preço "congelado" no momento da compra
                price_at_time = variation.product.current_price
                total_price += price_at_time * quantity
                
                # *** AQUI SUBTRAI O ESTOQUE ***
                variation.stock -= quantity
                db.session.add(variation)
                
                # Cria o OrderItem (o registro permanente do item)
                new_item = OrderItem(
                    order=novo_pedido, 
                    variation=variation, 
                    quantity=quantity, 
                    price_per_item=price_at_time
                )
                db.session.add(new_item)
                items_for_message.append(f"{quantity}x {variation.product.name} ({variation.size})")

            # Agora atualiza o pedido com o preço final
            novo_pedido.total_price = total_price
            
            # Monta a URL do WhatsApp com o ID do Pedido
            whatsapp_message_lines = [
                f"Olá! Gostaria de fazer o seguinte pedido:\n",
                f"*(Nº do Pedido: {novo_pedido.id})*\n"
            ]
            for var_id_str, quantity in cart_session.items():
                 variation = Variation.query.get(var_id_str)
                 subtotal = variation.product.current_price * quantity
                 whatsapp_message_lines.append(
                    f"- {quantity}x {variation.product.name} (Tamanho: {variation.size}) - R$ {subtotal:.2f}"
                 )
            whatsapp_message_lines.append(f"\n*Total: R$ {total_price:.2f}*")
            whatsapp_message = "\n".join(whatsapp_message_lines)

            whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={url_escape(whatsapp_message)}"
            novo_pedido.whatsapp_url = whatsapp_url
            
            # 3. Incrementa a estatística de "checkout"
            stat = get_stat('total_checkouts_whatsapp')
            stat.value += 1
            
            # 4. Salva tudo no banco
            db.session.commit()
            
            # 5. Limpa o carrinho
            session.pop('cart', None)
            session.pop('whatsapp_message', None)
            session.modified = True
            
            # 6. Redireciona o usuário para o WhatsApp
            flash(f'Seu pedido (Nº {novo_pedido.id}) foi registrado! Estamos te redirecionando para o WhatsApp.', 'success')
            return redirect(whatsapp_url)

        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao processar seu pedido: {e}. Tente novamente.', 'danger')
            return redirect(url_for('carrinho'))

    
    @app.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
    def adicionar_carrinho(produto_id):
        if 'cart' not in session:
            session['cart'] = {}
        
        variation_id = request.form.get('variation_id')
        produto = Product.query.get_or_404(produto_id) # <-- Já busca o produto

        if not variation_id:
             flash('Por favor, selecione um tamanho.', 'danger')
             return redirect(url_for('produto_detalhe', slug=produto.slug))
        
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity < 1:
                quantity = 1
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
            flash(f'Desculpe, temos apenas {variacao.stock} unidades de {produto.name} ({variacao.size}) em estoque. (Você já tem {current_in_cart} no carrinho).', 'danger')
        else:
            session['cart'][var_id_str] = total_wanted
            session.modified = True 
            
            # --- ADICIONADO: Rastreamento de Adição ao Carrinho ---
            try:
                produto.cart_add_count += 1
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao salvar contagem de carrinho: {e}")
            # --- FIM DA ADIÇÃO ---
            
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

    # --- Rotas de Autenticação (Login/Logout) ---

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Se o usuário já estiver logado, redireciona para o admin
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
                
            # Busca o usuário pelo email
            user = User.query.filter_by(email=email).first()
                
            # Verifica se o usuário existe e se a senha está correta
            if user and user.check_password(senha):
                login_user(user) # <-- Função do Flask-Login que cria a sessão
                    
                # Redireciona para a página 'next' se ela existir (ex: /admin)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin.index'))
            else:
                flash('Email ou senha inválidos. Tente novamente.', 'danger')
                    
        return render_template('login.html') # <-- Renderiza seu login.html

    @app.route('/logout')
    def logout():
        logout_user() # <-- Função do Flask-Login que limpa a sessão
        flash('Você saiu da sua conta.', 'success')
        return redirect(url_for('login'))

    # --- Fim da Função create_app ---
    return app

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    app = create_app()
    # Não precisamos mais do db.create_all() aqui
    # O Flask-Migrate cuida disso
    app.run(debug=True, port=5001)
