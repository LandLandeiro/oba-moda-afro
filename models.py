# models.py
from extensions import db

# Modelos para o Header
class HeaderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False, default="#")
    order = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.name

# Modelos para as Categorias Circulares (Bolinhas)
class CircularCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    link_url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    section = db.Column(db.Integer, default=1) 

    def __str__(self):
        return f"{self.name} (Seção {self.section})"

# Modelos para os Banners do Carrossel
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url_desktop = db.Column(db.String(200), nullable=False)
    image_url_mobile = db.Column(db.String(200), nullable=True)
    link_url = db.Column(db.String(200), default="#")
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.title or f"Banner {self.id}"

# Modelos para Produtos
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)

    def __str__(self):
        return self.name

# Tabela de associação (não precisa de __str__)
product_section_association = db.Table('product_section_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('product_section.id'))
)

# Modelo para a Seção de Produtos (ex: "Destaques")
class ProductSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Destaques")
    products = db.relationship('Product', secondary=product_section_association,
                               backref=db.backref('sections', lazy='dynamic'))

    def __str__(self):
        return self.title

# Modelo para Seções de Texto Genéricas (ex: "Sobre Nós")
class TextSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, default='sobre-nos')
    title = db.Column(db.String(150), nullable=False, default="Sobre Nós")
    content = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.title

# Modelo para Links do Footer
class FooterLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    column = db.Column(db.Integer, default=1)

    def __str__(self):
        return f"{self.title} (Coluna {self.column})"