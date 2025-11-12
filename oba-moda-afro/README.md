# Obá Moda Afro - Plataforma de E-commerce

## 📌 Descrição do Projeto

Plataforma completa de e-commerce desenvolvida com **Flask** para a marca **Obá Moda Afro**. O sistema integra uma vitrine de produtos moderna e responsiva com um painel administrativo robusto, incluindo dashboard de análise de vendas e gerenciamento automatizado de estoque.

---

## 📑 Sumário

- [Visão Geral das Funcionalidades](#visão-geral-das-funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração Inicial](#configuração-inicial)
- [Execução](#execução)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Documentação Técnica](#documentação-técnica)
- [Gerenciamento de Banco de Dados](#gerenciamento-de-banco-de-dados)

---

## 🎯 Visão Geral das Funcionalidades

### 🛍️ Plataforma Pública (Loja Virtual)

- **Design Responsivo**: Interface moderna construída com Bootstrap 5, otimizada para dispositivos móveis, tablets e desktops
- **Vitrine Dinâmica**: Página inicial com carrossel de banners, categorias circulares e seções de produtos personalizáveis via administração
- **Navegação por Categorias**: Browsing intuitivo de produtos organizados por categoria (`/categoria/<slug>`)
- **Página de Detalhes**: Visualização completa com preço promocional, descrição em HTML rico e seleção de variações (tamanho/cor)
- **Carrinho de Compras**: Sistema de carrinho persistente em sessão com atualização em tempo real
- **Integração WhatsApp**: Fluxo de checkout que:
  - Valida disponibilidade de estoque em tempo real
  - Reserva produtos imediatamente após confirmação
  - Cria registro de pedido no banco de dados
  - Redireciona cliente ao WhatsApp com detalhes do pedido

### 🔐 Painel Administrativo (Flask-Admin)

- **Autenticação Segura**: Sistema de login com criptografia de senha (bcrypt) e sessão gerenciada
- **Dashboard de Analytics**:
  - Receita total com filtro de data
  - Total de leads gerados via WhatsApp
  - Taxa de conversão (leads → vendas concluídas)
  - Gráficos de receita diária e status de pedidos
  - Dashboard de gestão de estoque com alertas
  
- **Gerenciamento de Produtos**:
  - CRUD completo com upload de imagens
  - Associação a múltiplas categorias
  - Gerenciamento de variações (tamanho/estoque) inline
  - Duplicação em massa de produtos
  - Editor de descrição em HTML rico (CKEditor)

- **Sistema de Promoções**:
  - Campanhas com desconto percentual
  - Datas de início e fim configuráveis
  - Associação de múltiplos produtos por campanha
  - Cálculo automático de preço promocional

- **Gerenciamento de Estoque**:
  - Alertas de baixo estoque (1-5 unidades)
  - Listagem de produtos esgotados
  - **Restock Automático**: Devolução automática de estoque ao cancelar pedido
  - Rastreamento de flag `restocked` para evitar duplicação

- **Gerenciamento de Conteúdo**:
  - Configuração de banners com links internos ou externos
  - Categorias circulares para homepage
  - Seções de produtos na vitrine
  - Links customizáveis do rodapé (agrupados por coluna)
  - Seções de texto (ex: "Sobre Nós")

---

## 📂 Estrutura do Projeto

```
oba-moda-afro/
│
├── app.py                    # Aplicação principal Flask
├── models.py                 # Modelos de dados (SQLAlchemy)
├── admin.py                  # Configuração do painel administrativo
├── extensions.py             # Inicialização de extensões
├── create_admin.py           # Script de criação do usuário admin
├── requirements.txt          # Dependências do projeto
├── oba_afro.db               # Banco de dados SQLite
│
├── migrations/               # Histórico de migrações (Flask-Migrate)
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── b43f792be303_adiciona_orderitem_e_sistema_de_restock.py
│
├── static/
│   ├── css/
│   │   ├── style.css         # Estilos principais
│   │   └── admin_custom.css  # Customizações do painel admin
│   ├── js/
│   │   └── script.js         # Scripts JavaScript
│   └── uploads/              # Imagens de produtos, banners, etc.
│
└── templates/
    ├── base.html             # Template base (header, footer)
    ├── index.html            # Página inicial
    ├── produtos.html         # Listagem de produtos
    ├── categoria_produtos.html
    ├── produto_detalhe.html  # Página de detalhes
    ├── carrinho.html         # Página do carrinho
    ├── login.html            # Página de login
    └── admin/
        ├── index.html        # Dashboard customizado
        └── produtos.html
```

---

## 🛠️ Tecnologias

### Backend

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| Python | 3.7+ | Linguagem principal |
| Flask | Latest | Microframework web |
| Flask-SQLAlchemy | Latest | ORM e abstração de banco |
| Flask-Migrate | Latest | Versionamento de banco de dados |
| Flask-Admin | Latest | Interface administrativa CRUD |
| Flask-Login | Latest | Gerenciamento de sessão/autenticação |
| Flask-Bcrypt | Latest | Hashing de senhas |
| Flask-CKEditor | Latest | Editor de texto rico |
| SQLAlchemy | Latest | ORM avançado |
| python-slugify | Latest | Geração de URLs amigáveis |
| bleach | Latest | Sanitização de HTML |

### Frontend

| Tecnologia | Propósito |
|-----------|----------|
| HTML5 | Estrutura de templates |
| Jinja2 | Template engine |
| CSS3 | Estilização |
| Bootstrap 5 | Framework responsivo |
| JavaScript (ES6+) | Interatividade |
| Chart.js | Gráficos dos dashboards |
| Bootstrap Icons | Ícones |

### Banco de Dados

| Componente | Especificação |
|-----------|--------------|
| SGBD | SQLite 3 |
| Arquivo | `oba_afro.db` |
| Versionamento | Flask-Migrate / Alembic |

---

## ⚙️ Instalação

### Pré-requisitos

- **Python 3.7 ou superior**
- **pip** (gerenciador de pacotes)
- **Git** (opcional, para clonar o repositório)

### Passo 1: Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd oba-moda-afro
```

### Passo 2: Criar e Ativar Ambiente Virtual

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Variável de Ambiente

**Windows:**
```bash
set FLASK_APP=app.py
```

**macOS/Linux:**
```bash
export FLASK_APP=app.py
```

---

## 🔧 Configuração Inicial

### Passo 1: Inicializar o Banco de Dados

Se for a primeira execução:

```bash
flask db init
flask db migrate -m "Migração inicial"
flask db upgrade
```

Se o banco já existe (após clonar o repositório):

```bash
flask db upgrade
```

### Passo 2: Criar Usuário Administrador

```bash
python create_admin.py
```

**Credenciais padrão:**
- **Email**: `obaafro1`
- **Senha**: `Ob4afr0`

⚠️ **Altere estas credenciais após o primeiro login**.

---

## 🚀 Execução

### Iniciar a Aplicação

```bash
python app.py
```

### Acessar a Plataforma

| Seção | URL |
|-------|-----|
| Loja Virtual | [http://127.0.0.1:5001](http://127.0.0.1:5001) |
| Login Admin | [http://127.0.0.1:5001/login](http://127.0.0.1:5001/login) |
| Painel Admin | [http://127.0.0.1:5001/admin](http://127.0.0.1:5001/admin) |

---

## 🏗️ Arquitetura do Sistema

### Fluxo de Checkout (Reserva de Estoque)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CLIENTE                                                      │
│    └─ Clica "Finalizar Pedido" (carrinho.html)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│ 2. SERVIDOR (app.py - Rota /checkout/criar-pedido)             │
│                                                                  │
│    2.1 Inicia transação (db.session)                            │
│    2.2 Valida estoque disponível para cada item                 │
│    2.3 Se validação OK:                                         │
│         ├─ Subtrai quantidade do Variation.stock                │
│         ├─ Cria registro Order (status='Pendente')              │
│         ├─ Cria registros OrderItem para cada produto           │
│         ├─ Salva no banco (db.session.commit())                 │
│         └─ Limpa carrinho da sessão                             │
│    2.4 Se erro:                                                 │
│         └─ Desfaz transação (db.session.rollback())             │
│                                                                  │
│    2.5 Redireciona para WhatsApp com ID do pedido               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│ 3. ADMIN (Painel Flask-Admin)                                   │
│    └─ Edita status do pedido (#ID) para:                        │
│       • "Concluído" → Registra venda nos gráficos               │
│       • "Cancelado" → on_model_change() ativa restock           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│ 4. RESTOCK AUTOMÁTICO (admin.py - OrderView)                    │
│                                                                  │
│    4.1 Se status = 'Cancelado' AND restocked = False:           │
│         ├─ Loop: Lê cada OrderItem do pedido                    │
│         ├─ Adiciona item.quantity ao Variation.stock            │
│         ├─ Marca order.restocked = True                         │
│         └─ Salva no banco                                       │
│                                                                  │
│    4.2 Se status ≠ 'Cancelado' AND restocked = True:            │
│         ├─ Verifica se há estoque disponível                    │
│         ├─ Re-subtrai do estoque                                │
│         ├─ Marca order.restocked = False                        │
│         └─ Salva no banco                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💻 Documentação Técnica

### 1. Modelos de Dados (`models.py`)

#### Tabelas de Associação (Muitos-para-Muitos)

```python
# Produto ↔ Categoria
product_category_association = db.Table(
    'product_category_association',
    db.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

# Promoção ↔ Produto
promotion_product_association = db.Table(
    'promotion_product_association',
    db.metadata,
    db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)
```

#### Modelo de Pedido e Itens

```python
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Pendente')  # Pendente, Concluído, Cancelado
    restocked = db.Column(db.Boolean, default=False)  # Flag de segurança
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    variation_id = db.Column(db.Integer, db.ForeignKey('variation.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)  # Preço congelado
```

#### Propriedades Inteligentes

```python
class Product(db.Model):
    # ...
    
    @property
    def active_promotion(self):
        """Retorna a promoção ativa (se houver)"""
        for promo in self.promotions:
            if promo.is_currently_active:
                return promo
        return None
    
    @property
    def current_price(self):
        """Preço com desconto (se houver promoção ativa)"""
        promo = self.active_promotion
        if promo:
            discount = 1.0 - (promo.discount_percent / 100.0)
            return round(self.price * discount, 2)
        return self.price
    
    @property
    def total_stock(self):
        """Soma de estoque de todas as variações"""
        return sum(var.stock for var in self.variations) if self.variations else 0
```

---

### 2. Aplicação Principal (`app.py`)

#### Context Processor - Dados Globais

```python
@app.context_processor
def inject_global_data():
    """Injeta dados disponíveis em todos os templates"""
    
    # Categorias do header
    header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
    
    # Contagem de itens no carrinho
    cart = session.get('cart', {})
    cart_item_count = sum(cart.values())
    
    # Links do rodapé agrupados por coluna
    footer_links_db = FooterLink.query.order_by(FooterLink.column, FooterLink.order).all()
    footer_links_grouped = {}
    for link in footer_links_db:
        if link.column not in footer_links_grouped:
            footer_links_grouped[link.column] = []
        footer_links_grouped[link.column].append(link)
    
    return {
        'now': datetime.datetime.now(),
        'header_categories': header_categories,
        'cart_item_count': cart_item_count,
        'footer_links': footer_links_grouped,
        'current_user': current_user
    }
```

#### Rota de Checkout - Abate de Estoque

```python
@app.route('/checkout/criar-pedido', methods=['POST'])
def criar_pedido():
    """
    Processa o checkout do pedido:
    1. Valida estoque
    2. Subtrai quantidade
    3. Cria registros de pedido
    4. Redireciona ao WhatsApp
    """
    
    cart_session = session.get('cart', {})
    
    if not cart_session:
        flash('Carrinho vazio', 'warning')
        return redirect(url_for('carrinho'))
    
    # VALIDAÇÃO: Checa estoque antes de subtrair
    for var_id_str, quantity in cart_session.items():
        variation = Variation.query.get(var_id_str)
        if not variation or variation.stock < quantity:
            flash(f'Estoque insuficiente para {variation.product.name}', 'danger')
            return redirect(url_for('carrinho'))
    
    try:
        # PROCESSAMENTO: Subtrai estoque e cria pedido
        novo_pedido = Order(total_price=0, status='Pendente')
        db.session.add(novo_pedido)
        
        total_price = 0
        
        for var_id_str, quantity in cart_session.items():
            variation = Variation.query.get(var_id_str)
            price_at_time = variation.product.current_price
            
            # ⭐ SUBTRAI O ESTOQUE
            variation.stock -= quantity
            db.session.add(variation)
            
            # Cria OrderItem
            new_item = OrderItem(
                order=novo_pedido,
                variation=variation,
                quantity=quantity,
                price_per_item=price_at_time
            )
            db.session.add(new_item)
            total_price += price_at_time * quantity
        
        novo_pedido.total_price = total_price
        
        # Gera URL do WhatsApp
        whatsapp_message = f"Pedido #{novo_pedido.id}: R$ {total_price:.2f}"
        whatsapp_url = f"https://wa.me/+5515997479931?text={url_escape(whatsapp_message)}"
        novo_pedido.whatsapp_url = whatsapp_url
        
        db.session.commit()
        session.pop('cart', None)
        
        flash(f'Pedido #{novo_pedido.id} criado! Redirecionando...', 'success')
        return redirect(whatsapp_url)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao processar pedido: {e}', 'danger')
        return redirect(url_for('carrinho'))
```

---

### 3. Painel Administrativo (`admin.py`)

#### Sistema de Restock Automático

```python
class OrderView(SecureModelView):
    """
    Gerenciamento de pedidos com restock automático
    """
    
    def on_model_change(self, form, model, is_created):
        """
        Hook executado ao salvar um pedido.
        Implementa lógica de restock automático.
        """
        
        if not is_created:  # Se está EDITANDO (não criando novo)
            
            # LÓGICA 1: CANCELAMENTO → Devolver Estoque
            if model.status == 'Cancelado' and not model.restocked:
                try:
                    for item in model.order_items:
                        # ⭐ ADICIONA O ESTOQUE
                        item.variation.stock += item.quantity
                        db.session.add(item.variation)
                    
                    model.restocked = True  # Flag de segurança
                    flash("Estoque devolvido com sucesso!", "success")
                    
                except Exception as e:
                    flash(f"Erro ao devolver estoque: {e}", "danger")
            
            # LÓGICA 2: RE-ATIVAÇÃO → Subtrair Novamente
            elif model.status != 'Cancelado' and model.restocked:
                try:
                    # Verifica se há estoque disponível
                    for item in model.order_items:
                        if item.variation.stock < item.quantity:
                            flash("Estoque insuficiente para re-ativar", "error")
                            model.status = 'Cancelado'
                            return super().on_model_change(form, model, is_created)
                    
                    # Subtrai novamente
                    for item in model.order_items:
                        item.variation.stock -= item.quantity
                        db.session.add(item.variation)
                    
                    model.restocked = False
                    flash("Estoque re-subtraído", "warning")
                    
                except Exception as e:
                    flash(f"Erro ao re-subtrair: {e}", "danger")
        
        super().on_model_change(form, model, is_created)
```

#### Dashboard de Analytics

```python
class SecureAdminIndexView(AdminIndexView):
    """Dashboard com KPIs e filtros de data"""
    
    @expose('/')
    def index(self):
        # Processamento de filtros de data
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Cálculo de KPIs
        receita_total = db.session.query(func.sum(Order.total_price))\
            .filter(Order.status == 'Concluído')\
            .filter(Order.created_at.between(start_date, end_date))\
            .scalar()
        
        total_leads = Order.query\
            .filter(Order.created_at.between(start_date, end_date))\
            .count()
        
        # Gráficos
        dados_receita_linha = self._gerar_grafico_receita(start_date, end_date)
        dados_status_pizza = self._gerar_grafico_status(start_date, end_date)
        
        # Gestão de estoque
        low_stock_products = [p for p in Product.query.all() 
                             if p.total_stock <= 5 and p.total_stock > 0]
        
        return self.render(self._template, 
                          receita_total=receita_total,
                          total_leads=total_leads,
                          dados_receita_linha=dados_receita_linha,
                          dados_status_pizza=dados_status_pizza,
                          low_stock_products=low_stock_products)
```

---

## 🌍 Gerenciamento de Banco de Dados

### Usando Flask-Migrate

⚠️ **IMPORTANTE**: Este projeto usa **Flask-Migrate**. Nunca delete `oba_afro.db` manualmente para fazer alterações nos modelos.

### Adicionar um Novo Campo ao Model

**Exemplo**: Adicionar campo `telefone` ao model `User`

#### 1. Editar o Model

```python
# models.py
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)  # ← NOVO CAMPO
```

#### 2. Gerar Migração

```bash
flask db migrate -m "Adiciona campo telefone ao User"
```

Isso cria um novo arquivo em `migrations/versions/`.

#### 3. Revisar e Aplicar

```bash
# Revisar o arquivo criado (segurança)
cat migrations/versions/XXXXX_adiciona_campo_telefone_ao_user.py

# Aplicar ao banco
flask db upgrade
```

#### 4. Pronto!

O campo está agora no banco de dados sem perder nenhum dado existente.

### Reverter Última Migração

```bash
flask db downgrade
```

### Ver Histórico de Migrações

```bash
flask db history
```

---

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação de cada tecnologia:

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Flask-Admin Documentation](https://flask-admin.readthedocs.io/)

---

## 📄 Licença

Este projeto foi desenvolvido para a marca **Obá Moda Afro**.

---

**Última atualização**: Dezembro de 2024
