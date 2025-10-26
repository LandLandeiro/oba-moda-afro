from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Produto, ConteudoSite
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

db.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def criar_tabelas():
    db.create_all()
    # Criar usuário admin padrão se não existir
    if not Usuario.query.filter_by(email='admin@loja.com').first():
        admin = Usuario(
            nome='Administrador',
            email='admin@loja.com',
            senha=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
    
    # Criar conteúdo padrão se não existir
    if not ConteudoSite.query.first():
        conteudo = ConteudoSite(
            titulo_principal='Bem-vindo à Nossa Loja',
            subtitulo='Produtos de qualidade com os melhores preços',
            sobre_titulo='Sobre Nós',
            sobre_texto='Somos uma loja comprometida em oferecer os melhores produtos para você.',
            whatsapp='5511999999999'
        )
        db.session.add(conteudo)
        db.session.commit()

app.before_request_funcs = {None: [criar_tabelas]}

# ========== ROTAS PÚBLICAS ==========
@app.route('/')
def index():
    conteudo = ConteudoSite.query.first()
    produtos_destaque = Produto.query.filter_by(ativo=True).limit(6).all()
    return render_template('index.html', conteudo=conteudo, produtos=produtos_destaque)

@app.route('/produtos')
def produtos():
    todos_produtos = Produto.query.filter_by(ativo=True).all()
    return render_template('produtos.html', produtos=todos_produtos)

@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', {})
    itens = []
    total = 0
    
    for produto_id, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if produto:
            subtotal = produto.preco * quantidade
            itens.append({
                'produto': produto,
                'quantidade': quantidade,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('carrinho.html', itens=itens, total=total)

@app.route('/adicionar_carrinho/<int:produto_id>')
def adicionar_carrinho(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    if 'carrinho' not in session:
        session['carrinho'] = {}
    
    carrinho = session['carrinho']
    produto_id_str = str(produto_id)
    
    if produto_id_str in carrinho:
        carrinho[produto_id_str] += 1
    else:
        carrinho[produto_id_str] = 1
    
    session['carrinho'] = carrinho
    session.modified = True  # Força o Flask a salvar a sessão
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    return redirect(request.referrer or url_for('produtos'))

@app.route('/remover_carrinho/<int:produto_id>')
def remover_carrinho(produto_id):
    if 'carrinho' in session:
        carrinho = session['carrinho']
        produto_id_str = str(produto_id)
        if produto_id_str in carrinho:
            del carrinho[produto_id_str]
            session['carrinho'] = carrinho
            session.modified = True  # Força o Flask a salvar a sessão
            flash('Item removido do carrinho.', 'info')
    return redirect(url_for('carrinho'))

@app.route('/atualizar_quantidade/<int:produto_id>/<int:quantidade>')
def atualizar_quantidade(produto_id, quantidade):
    if 'carrinho' in session:
        carrinho = session['carrinho']
        produto_id_str = str(produto_id)
        if quantidade > 0:
            carrinho[produto_id_str] = quantidade
        else:
            del carrinho[produto_id_str]
        session['carrinho'] = carrinho
        session.modified = True  # Força o Flask a salvar a sessão
    return redirect(url_for('carrinho'))

@app.route('/finalizar_compra')
def finalizar_compra():
    carrinho = session.get('carrinho', {})
    session.modified = True  # Força o Flask a salvar a sessão
    if not carrinho:
        flash('Seu carrinho está vazio!', 'warning')
        return redirect(url_for('produtos'))
    
    conteudo = ConteudoSite.query.first()
    whatsapp = conteudo.whatsapp if conteudo else '5511999999999'
    
    mensagem = "Olá! Gostaria de fazer um pedido:\n\n"
    total = 0
    
    for produto_id, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if produto:
            subtotal = produto.preco * quantidade
            total += subtotal
            mensagem += f"• {produto.nome} - {quantidade}x R$ {produto.preco:.2f} = R$ {subtotal:.2f}\n"
    
    mensagem += f"\n*Total: R$ {total:.2f}*"
    
    # Limpar carrinho
    session.pop('carrinho', None)
    
    # Redirecionar para WhatsApp
    import urllib.parse
    mensagem_encoded = urllib.parse.quote(mensagem)
    whatsapp_url = f"https://wa.me/{whatsapp}?text={mensagem_encoded}"
    
    return redirect(whatsapp_url)

# ========== AUTENTICAÇÃO ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

# ========== ÁREA ADMINISTRATIVA ==========
@app.route('/admin')
@login_required
def admin_dashboard():
    total_produtos = Produto.query.count()
    produtos_ativos = Produto.query.filter_by(ativo=True).count()
    return render_template('admin/dashboard.html', 
                         total_produtos=total_produtos,
                         produtos_ativos=produtos_ativos)

@app.route('/admin/produtos')
@login_required
def admin_produtos():
    produtos = Produto.query.all()
    return render_template('admin/produtos.html', produtos=produtos)

@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@login_required
def admin_produto_novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = float(request.form.get('preco'))
        estoque = int(request.form.get('estoque', 0))
        ativo = request.form.get('ativo') == 'on'
        
        imagem_filename = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                imagem_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))
        
        produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            imagem=imagem_filename,
            ativo=ativo
        )
        
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    return render_template('admin/produto_form.html', produto=None)

@app.route('/admin/produto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_produto_editar(id):
    produto = Produto.query.get_or_404(id)
    
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.descricao = request.form.get('descricao')
        produto.preco = float(request.form.get('preco'))
        produto.estoque = int(request.form.get('estoque', 0))
        produto.ativo = request.form.get('ativo') == 'on'
        
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                # Remover imagem antiga se existir
                if produto.imagem:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], produto.imagem)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                imagem_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))
                produto.imagem = imagem_filename
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    return render_template('admin/produto_form.html', produto=produto)

@app.route('/admin/produto/deletar/<int:id>')
@login_required
def admin_produto_deletar(id):
    produto = Produto.query.get_or_404(id)
    
    # Remover imagem se existir
    if produto.imagem:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], produto.imagem)
        if os.path.exists(img_path):
            os.remove(img_path)
    
    db.session.delete(produto)
    db.session.commit()
    
    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('admin_produtos'))

@app.route('/admin/conteudo', methods=['GET', 'POST'])
@login_required
def admin_conteudo():
    conteudo = ConteudoSite.query.first()
    
    if request.method == 'POST':
        conteudo.titulo_principal = request.form.get('titulo_principal')
        conteudo.subtitulo = request.form.get('subtitulo')
        conteudo.sobre_titulo = request.form.get('sobre_titulo')
        conteudo.sobre_texto = request.form.get('sobre_texto')
        conteudo.whatsapp = request.form.get('whatsapp')
        
        # Upload de imagem hero
        if 'imagem_hero' in request.files:
            file = request.files['imagem_hero']
            if file and file.filename and allowed_file(file.filename):
                if conteudo.imagem_hero:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], conteudo.imagem_hero)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                imagem_filename = f"hero_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))
                conteudo.imagem_hero = imagem_filename
        
        db.session.commit()
        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('admin_conteudo'))
    
    return render_template('admin/conteudo.html', conteudo=conteudo)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
