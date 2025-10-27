# models.py
from extensions import db
from sqlalchemy.orm import relationship

# --- Modelos existentes (sem alteração) ---
class HeaderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False, default="#")
    order = db.Column(db.Integer, default=0)
    def __str__(self): return self.name

class CircularCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    link_url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    section = db.Column(db.Integer, default=1) 
    def __str__(self): return f"{self.name} (Seção {self.section})"

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url_desktop = db.Column(db.String(200), nullable=False)
    image_url_mobile = db.Column(db.String(200), nullable=True)
    link_url = db.Column(db.String(200), default="#")
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    def __str__(self): return self.title or f"Banner {self.id}"

class TextSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, default='sobre-nos')
    title = db.Column(db.String(150), nullable=False, default="Sobre Nós")
    content = db.Column(db.Text, nullable=True)
    def __str__(self): return self.title

class FooterLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    column = db.Column(db.Integer, default=1)
    def __str__(self): return f"{self.title} (Coluna {self.column})"

# --- Modelos de Produto Modificados ---

# Novo Modelo para Variações (Tamanho/Estoque)
class Variation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)  # Ex: "P", "M", "G", "38"
    stock = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.stock} unid.)"

# Modelo de Produto Atualizado
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True) # Adicionado
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True) # Renomeado de image_url e permite nulo
    slug = db.Column(db.String(150), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True) # Adicionado

    # Relação com Variações
    variations = relationship('Variation', backref='product', lazy=True, cascade='all, delete-orphan')

    # Propriedade para calcular o estoque total
    @property
    def total_stock(self):
        if not self.variations:
            return 0
        return sum(var.stock for var in self.variations)

    def __str__(self):
        return self.name

# Modelos de Seção de Produto (mantidos para a index)
product_section_association = db.Table('product_section_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('product_section.id'))
)

class ProductSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Destaques")
    products = relationship('Product', secondary=product_section_association,
                            backref=db.backref('sections', lazy='dynamic'))
    def __str__(self): return self.title