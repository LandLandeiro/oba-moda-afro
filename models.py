# models.py
from extensions import db
from sqlalchemy.orm import relationship

# --- 1. NOVA TABELA DE ASSOCIAÇÃO (Muitos-para-Muitos) ---
# Esta tabela "liga" produtos a categorias
product_category_association = db.Table('product_category_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# --- 2. MODELO DE CATEGORIA ATUALIZADO ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relação "muitos-para-muitos"
    products = relationship('Product', 
                            secondary=product_category_association,
                            back_populates='categories')

    def __str__(self):
        return self.name

# Modelos para o Header (sem alterações)
class HeaderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False, default="#")
    order = db.Column(db.Integer, default=0)
    def __str__(self): return self.name

# Modelos para as Categorias Circulares (Bolinhas) (sem alterações)
class CircularCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    link_url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    section = db.Column(db.Integer, default=1) 
    def __str__(self): return f"{self.name} (Seção {self.section})"

# Modelos para os Banners do Carrossel (sem alterações)
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url_desktop = db.Column(db.String(200), nullable=False)
    image_url_mobile = db.Column(db.String(200), nullable=True)
    link_url = db.Column(db.String(200), default="#")
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    def __str__(self): return self.title or f"Banner {self.id}"

# --- 3. MODELO DE PRODUTO ATUALIZADO ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    # --- REMOVIDO o 'category_id' e 'category' (um-para-muitos) ---
    
    # --- ADICIONADO o 'categories' (muitos-para-muitos) ---
    categories = relationship('Category',
                              secondary=product_category_association,
                              back_populates='products')

    # Relação com Variações (sem alterações)
    variations = relationship('Variation', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def total_stock(self):
        if not self.variations:
            return 0
        return sum(var.stock for var in self.variations)

    def __str__(self):
        return self.name

# Novo Modelo para Variações (Tamanho/Estoque) (sem alterações)
class Variation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.stock} unid.)"

# Tabela de associação (para seções da Home) (sem alterações)
product_section_association = db.Table('product_section_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('product_section.id'))
)

# Modelo para a Seção de Produtos (ex: "Destaques") (sem alterações)
class ProductSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Destaques")
    products = db.relationship('Product', secondary=product_section_association,
                               backref=db.backref('sections', lazy='dynamic'))
    def __str__(self): return self.title

# Modelo para Seções de Texto Genéricas (ex: "Sobre Nós") (sem alterações)
class TextSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, default='sobre-nos')
    title = db.Column(db.String(150), nullable=False, default="Sobre Nós")
    content = db.Column(db.Text, nullable=True)
    def __str__(self): return self.title

# Modelo para Links do Footer (sem alterações)
class FooterLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    column = db.Column(db.Integer, default=1)
    def __str__(self): return f"{self.title} (Coluna {self.column})"