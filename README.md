# 🛒 Sistema de Loja Virtual - Flask

Sistema completo de e-commerce desenvolvido em Flask, com duas interfaces distintas: uma área pública moderna para clientes e um dashboard administrativo profissional.

---

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Instalação e Execução](#instalação-e-execução)
5. [Arquitetura do Sistema](#arquitetura-do-sistema)
6. [Explicação do Código](#explicação-do-código)
7. [Funcionalidades Detalhadas](#funcionalidades-detalhadas)
8. [Conceitos Aplicados](#conceitos-aplicados)
9. [Customização](#customização)

---

## 🎯 Visão Geral

Este projeto é uma loja virtual completa que demonstra conceitos fundamentais de desenvolvimento web:

### 🛍️ **Área Pública (E-commerce)**
- Design moderno e responsivo
- Hero section com banner personalizável
- Catálogo de produtos com cards animados
- Carrinho de compras funcional
- Integração com WhatsApp para finalização

### 🔧 **Área Administrativa (Dashboard)**
- Interface estilo SaaS/aplicativo
- CRUD completo de produtos
- Upload e gerenciamento de imagens
- Edição de conteúdo do site
- Sistema de autenticação

---

## 📂 Estrutura do Projeto

```
loja_virtual/
│
├── app.py                      # ❤️ Aplicação principal Flask
├── models.py                   # 💾 Modelos do banco de dados
├── requirements.txt            # 📦 Dependências do projeto
├── README.md                   # 📖 Esta documentação
│
├── database.db                 # 🗄️ Banco SQLite (criado automaticamente)
│
├── static/                     # 🎨 Arquivos estáticos
│   ├── css/
│   │   └── style.css          # Estilos da aplicação
│   ├── js/
│   │   └── script.js          # JavaScript do front-end
│   └── uploads/               # Imagens enviadas pelos usuários
│
└── templates/                  # 📄 Templates HTML
    ├── base.html              # Template base (navbar, footer)
    ├── index.html             # Página inicial
    ├── produtos.html          # Catálogo de produtos
    ├── carrinho.html          # Carrinho de compras
    ├── login.html             # Login administrativo
    └── admin/                 # Templates da área admin
        ├── dashboard.html     # Dashboard principal
        ├── produtos.html      # Lista de produtos
        ├── produto_form.html  # Formulário de produto
        └── conteudo.html      # Editor de conteúdo
```

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 3.0.0** - Framework web minimalista
- **Flask-SQLAlchemy 3.1.1** - ORM para banco de dados
- **Werkzeug 3.0.1** - Utilitários (segurança, uploads)
- **SQLite** - Banco de dados embutido

### Frontend
- **HTML5** - Estrutura das páginas
- **CSS3** - Estilização e animações
- **JavaScript (ES6+)** - Interatividade

### Conceitos
- **MVC/MTV Pattern** - Separação de responsabilidades
- **RESTful Routes** - Padrão de rotas
- **Session Management** - Gerenciamento de sessões
- **Authentication** - Autenticação com hash de senha
- **File Upload** - Upload seguro de arquivos

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

**1. Clone ou extraia o projeto**
```bash
cd loja_virtual
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Execute a aplicação**
```bash
python app.py
```

**4. Acesse no navegador**
```
Área Pública:  http://localhost:5000
Área Admin:    http://localhost:5000/login
```

### Credenciais Padrão
```
Email: admin@loja.com
Senha: admin123
```

### Produtos de Exemplo
Na primeira execução, 6 produtos são criados automaticamente para teste.

---

## 🏗️ Arquitetura do Sistema

### Padrão MVC Adaptado

```
┌─────────────────────────────────────────┐
│           USUÁRIO / NAVEGADOR           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        TEMPLATES (Views - HTML)         │
│  ┌───────────────────────────────────┐  │
│  │  index.html, produtos.html, etc.  │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         APP.PY (Controller)             │
│  ┌───────────────────────────────────┐  │
│  │  Rotas, Lógica de Negócio         │  │
│  │  @app.route('/')                  │  │
│  │  @app.route('/produtos')          │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       MODELS.PY (Model - Dados)         │
│  ┌───────────────────────────────────┐  │
│  │  Produto, Usuario, ConteudoSite   │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          DATABASE.DB (SQLite)           │
└─────────────────────────────────────────┘
```

---

## 💻 Explicação do Código

### 1. `models.py` - Modelos de Dados

Este arquivo define a **estrutura do banco de dados** usando SQLAlchemy ORM.

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
```

**O que acontece aqui:**
- `db.Model` - Cada classe herda de Model e vira uma tabela
- `db.Column` - Define uma coluna na tabela
- `primary_key=True` - Chave primária (ID único)
- `unique=True` - Não permite valores duplicados
- `nullable=False` - Campo obrigatório

**Tabelas criadas:**
1. **Usuario** - Administradores do sistema
2. **Produto** - Produtos da loja
3. **ConteudoSite** - Textos e imagens do site

### 2. `app.py` - Aplicação Principal

#### Configuração Inicial

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
```

**Explicação:**
- `SECRET_KEY` - Usado para criptografar sessões
- `SQLALCHEMY_DATABASE_URI` - Localização do banco SQLite
- `UPLOAD_FOLDER` - Pasta para imagens enviadas

#### Decorators Personalizados

```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
```

**O que faz:**
- Verifica se o usuário está logado
- Protege rotas administrativas
- Redireciona para login se não autenticado

**Como usar:**
```python
@app.route('/admin')
@login_required  # ← Aplica a proteção
def admin_dashboard():
    return render_template('admin/dashboard.html')
```

#### Inicialização Automática

```python
@app.before_request
def criar_tabelas():
    db.create_all()  # Cria tabelas se não existirem
    
    # Cria usuário admin padrão
    if not Usuario.query.filter_by(email='admin@loja.com').first():
        admin = Usuario(
            nome='Administrador',
            email='admin@loja.com',
            senha=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
```

**O que acontece:**
- Executa antes de qualquer requisição
- Cria o banco de dados automaticamente
- Adiciona usuário admin se não existir
- Adiciona produtos de exemplo

### 3. Rotas Públicas

#### Página Inicial
```python
@app.route('/')
def index():
    conteudo = ConteudoSite.query.first()
    produtos_destaque = Produto.query.filter_by(ativo=True).limit(6).all()
    return render_template('index.html', 
                         conteudo=conteudo, 
                         produtos=produtos_destaque)
```

**Fluxo:**
1. Busca conteúdo do site no banco
2. Busca 6 produtos ativos
3. Passa dados para o template
4. Renderiza a página

#### Sistema de Carrinho

```python
@app.route('/adicionar_carrinho/<int:produto_id>')
def adicionar_carrinho(produto_id):
    # 1. Busca o produto no banco
    produto = Produto.query.get_or_404(produto_id)
    
    # 2. Cria carrinho na sessão se não existir
    if 'carrinho' not in session:
        session['carrinho'] = {}
    
    # 3. Converte ID para string (sessão só aceita strings)
    produto_id_str = str(produto_id)
    
    # 4. Adiciona ou incrementa quantidade
    if produto_id_str in carrinho:
        carrinho[produto_id_str] += 1
    else:
        carrinho[produto_id_str] = 1
    
    # 5. Salva no session e força atualização
    session['carrinho'] = carrinho
    session.modified = True  # ← IMPORTANTE!
    
    # 6. Mensagem de sucesso e redirect
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    return redirect(request.referrer or url_for('index'))
```

**Por que `session.modified = True`?**
- Flask não detecta mudanças em dicionários automaticamente
- Precisamos forçar a sessão a salvar
- Sem isso, o carrinho não persiste entre requisições

#### Visualizar Carrinho

```python
@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', {})
    itens = []
    total = 0
    
    # Para cada produto no carrinho
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
```

**Estrutura de dados:**
```python
# Session armazena assim:
session['carrinho'] = {
    '1': 2,    # Produto ID 1, quantidade 2
    '5': 1,    # Produto ID 5, quantidade 1
    '8': 3     # Produto ID 8, quantidade 3
}

# View transforma em:
itens = [
    {
        'produto': <Produto objeto>,
        'quantidade': 2,
        'subtotal': 199.80
    },
    # ...
]
```

#### Finalizar Compra (WhatsApp)

```python
@app.route('/finalizar_compra')
def finalizar_compra():
    carrinho = session.get('carrinho', {})
    
    # Monta mensagem formatada
    mensagem = "Olá! Gostaria de fazer um pedido:\n\n"
    
    for produto_id, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        subtotal = produto.preco * quantidade
        mensagem += f"• {produto.nome} - {quantidade}x"
        mensagem += f" R$ {produto.preco:.2f} = R$ {subtotal:.2f}\n"
    
    mensagem += f"\n*Total: R$ {total:.2f}*"
    
    # URL encode da mensagem
    import urllib.parse
    mensagem_encoded = urllib.parse.quote(mensagem)
    
    # Monta URL do WhatsApp
    whatsapp_url = f"https://wa.me/{whatsapp}?text={mensagem_encoded}"
    
    # Limpa carrinho e redireciona
    session['carrinho'] = {}
    session.modified = True
    
    return redirect(whatsapp_url)
```

**Resultado:**
```
https://wa.me/5511999999999?text=Ol%C3%A1!%20Gostaria%20de...
```

### 4. Autenticação

#### Login
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Busca usuário
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Verifica senha com hash
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('login.html')
```

**Segurança:**
- Senha NUNCA é armazenada em texto puro
- `generate_password_hash()` - Cria hash da senha
- `check_password_hash()` - Verifica senha sem descriptografar

### 5. CRUD de Produtos

#### Listar Produtos (Read)
```python
@app.route('/admin/produtos')
@login_required
def admin_produtos():
    produtos = Produto.query.all()
    return render_template('admin/produtos.html', produtos=produtos)
```

#### Criar Produto (Create)
```python
@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@login_required
def admin_produto_novo():
    if request.method == 'POST':
        # 1. Coleta dados do formulário
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = float(request.form.get('preco'))
        estoque = int(request.form.get('estoque', 0))
        ativo = request.form.get('ativo') == 'on'
        
        # 2. Processa upload de imagem
        imagem_filename = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename:
                # Sanitiza nome do arquivo
                filename = secure_filename(file.filename)
                # Adiciona timestamp para evitar conflitos
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                imagem_filename = f"{timestamp}_{filename}"
                # Salva arquivo
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                      imagem_filename))
        
        # 3. Cria objeto Produto
        produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            imagem=imagem_filename,
            ativo=ativo
        )
        
        # 4. Salva no banco
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    # GET - Mostra formulário vazio
    return render_template('admin/produto_form.html', produto=None)
```

**Upload de Arquivo:**
```python
# Arquivo original: "Minha Foto (1).jpg"
secure_filename("Minha Foto (1).jpg")  # → "Minha_Foto_1.jpg"

# Timestamp evita conflitos
"20250106123045_Minha_Foto_1.jpg"
```

#### Atualizar Produto (Update)
```python
@app.route('/admin/produto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_produto_editar(id):
    produto = Produto.query.get_or_404(id)
    
    if request.method == 'POST':
        # Atualiza campos
        produto.nome = request.form.get('nome')
        produto.preco = float(request.form.get('preco'))
        # ...
        
        # Se enviou nova imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename:
                # Remove imagem antiga
                if produto.imagem:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                           produto.imagem)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Salva nova imagem
                # ... (mesmo código de upload)
        
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('admin_produtos'))
    
    # GET - Mostra formulário preenchido
    return render_template('admin/produto_form.html', produto=produto)
```

#### Deletar Produto (Delete)
```python
@app.route('/admin/produto/deletar/<int:id>')
@login_required
def admin_produto_deletar(id):
    produto = Produto.query.get_or_404(id)
    
    # Remove imagem do disco
    if produto.imagem:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], produto.imagem)
        if os.path.exists(img_path):
            os.remove(img_path)
    
    # Remove do banco
    db.session.delete(produto)
    db.session.commit()
    
    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('admin_produtos'))
```

### 6. Templates (Jinja2)

#### Template Base
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Loja Virtual{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <!-- Navbar sempre presente -->
    </nav>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <!-- Flash messages -->
        {% endif %}
    {% endwith %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <!-- Footer sempre presente -->
    </footer>
</body>
</html>
```

#### Template Filho
```html
<!-- produtos.html -->
{% extends 'base.html' %}

{% block title %}Produtos - Loja Virtual{% endblock %}

{% block content %}
<div class="container">
    <h1>Nossos Produtos</h1>
    
    {% for produto in produtos %}
    <div class="produto-card">
        <img src="{{ url_for('static', filename='uploads/' + produto.imagem) }}">
        <h3>{{ produto.nome }}</h3>
        <p>R$ {{ "%.2f"|format(produto.preco) }}</p>
        <a href="{{ url_for('adicionar_carrinho', produto_id=produto.id) }}">
            Adicionar ao Carrinho
        </a>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

**Sintaxe Jinja2:**
- `{% %}` - Lógica (for, if, extends)
- `{{ }}` - Variáveis/expressões
- `{# #}` - Comentários

### 7. CSS - Estrutura

#### Reset e Base
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

#### Cards de Produto
```css
.produto-card {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    transition: transform 0.4s;
}

.produto-card::before {
    content: '';
    position: absolute;
    pointer-events: none;  /* ← Permite cliques através */
    z-index: 1;
}

.produto-card .btn {
    position: relative;
    z-index: 10;  /* ← Acima de tudo */
    cursor: pointer;
}
```

**Problema comum:**
- Elemento sobreposto bloqueando cliques
- **Solução:** `pointer-events: none` + `z-index`

### 8. JavaScript

#### Auto-hide Flash Messages
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
```

#### Preview de Imagem
```javascript
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Mostra preview da imagem
                const img = document.querySelector('.current-image img');
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});
```

---

## 🎓 Conceitos Aplicados

### 1. MVC/MTV Pattern

**Model (models.py)**
- Define estrutura de dados
- Regras de negócio
- Interação com banco

**View (templates/)**
- Apresentação visual
- HTML + CSS
- Interface do usuário

**Controller (app.py)**
- Lógica da aplicação
- Processa requisições
- Conecta Model e View

### 2. ORM (Object-Relational Mapping)

**Sem ORM:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (1,))
produto = cursor.fetchone()
```

**Com ORM:**
```python
produto = Produto.query.get(1)
```

**Vantagens:**
- Código mais legível
- Menos SQL manual
- Proteção contra SQL Injection
- Portabilidade entre bancos

### 3. Rotas RESTful

```
GET    /produtos           - Lista produtos
GET    /produto/novo       - Formulário novo
POST   /produto/novo       - Cria produto
GET    /produto/editar/1   - Formulário editar
POST   /produto/editar/1   - Atualiza produto
GET    /produto/deletar/1  - Deleta produto
```

### 4. Session Management

**O que são sessões?**
- Dados armazenados no servidor
- Identificados por cookie no navegador
- Persistem entre requisições

**Exemplo:**
```python
# Primeira requisição
session['usuario_id'] = 1

# Próxima requisição (mesma sessão)
if 'usuario_id' in session:
    usuario_logado = True
```

### 5. Template Inheritance

```
base.html (navbar, footer)
    ├── index.html (hero, produtos)
    ├── produtos.html (lista completa)
    └── carrinho.html (tabela carrinho)
```

**Vantagem:** Código reutilizável

### 6. Segurança

#### Hash de Senha
```python
# Ao criar usuário
senha_hash = generate_password_hash('admin123')
# Resultado: 'pbkdf2:sha256:...'

# Ao fazer login
check_password_hash(senha_hash, 'admin123')  # True
```

#### Upload Seguro
```python
filename = secure_filename(user_input)
# Remove caracteres perigosos: ../, \, etc.
```

#### Proteção CSRF
```python
app.config['SECRET_KEY'] = 'chave-aleatoria'
# Flask usa isso para assinar sessões
```

### 7. Flash Messages

```python
# No controller
flash('Produto salvo!', 'success')

# No template
{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        <div class="alert-{{ category }}">{{ message }}</div>
    {% endfor %}
{% endwith %}
```

