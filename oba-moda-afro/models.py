# models.py
from extensions import db, bcrypt
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime
from flask import url_for 

# --- 1. TABELAS DE ASSOCIAÇÃO ---
product_category_association = db.Table('product_category_association',
    db.metadata, 
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

promotion_product_association = db.Table('promotion_product_association',
    db.metadata,
    db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Promotion(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Ex: "Black Friday"
    is_active = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    discount_percent = db.Column(db.Float, default=0.0)
    products = relationship('Product',
                            secondary=promotion_product_association,
                            back_populates='promotions')
    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"
    @property
    def is_currently_active(self):
        if not self.is_active:
            return False
        now = datetime.datetime.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

class Category(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    products = relationship('Product', 
                            secondary=product_category_association,
                            back_populates='categories')
    def __str__(self):
        return self.name

class HeaderCategory(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    order = db.Column(db.Integer, default=0)
    category = db.relationship('Category', backref='header_links', lazy=True)
    def __str__(self):
        if self.category:
            return f"{self.name} (Links para: {self.category.name})"
        return self.name

class CircularCategory(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref='circular_links', lazy=True)
    order = db.Column(db.Integer, default=0)
    section = db.Column(db.Integer, default=1) 
    def __str__(self):
        if self.category:
            return f"{self.name} (Link: {self.category.name}) (Seção {self.section})"
        return f"{self.name} (Seção {self.section})"

class Banner(db.Model):
    # ... (Sem alteração - já corrigido) ...
    id = db.Column(db.Integer, primary_key=True)
    image_url_desktop = db.Column(db.String(200), nullable=False)
    image_url_mobile = db.Column(db.String(200), nullable=True)
    link_url = db.Column(db.String(200), default="#", nullable=True) 
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True) 
    product = db.relationship('Product', backref='banners', lazy=True)
    
    @property
    def final_link_url(self):
        if self.product and self.product.slug:
            try:
                return url_for('produto_detalhe', slug=self.product.slug)
            except RuntimeError:
                return f"/produto/{self.product.slug}"
        if self.link_url and self.link_url != "#":
            if self.link_url.startswith('http://') or self.link_url.startswith('https://'):
                return self.link_url
            return f"//{self.link_url}"
        return "#"

    def __str__(self): return self.title or f"Banner {self.id}"

class Product(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(150), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True)
    cart_add_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0) 
    categories = relationship('Category',
                              secondary=product_category_association,
                              back_populates='products')
    promotions = relationship('Promotion',
                              secondary=promotion_product_association,
                              back_populates='products')    
    variations = relationship('Variation', backref='product', lazy=True, cascade='all, delete-orphan')
    @property
    def active_promotion(self):
        if not self.promotions:
            return None
        for promo in self.promotions:
            if promo.is_currently_active:
                return promo
        return None
    @property
    def is_on_sale(self):
        return self.active_promotion is not None
    @property
    def current_price(self):
        promo = self.active_promotion
        if promo:
            discount_factor = 1.0 - (promo.discount_percent / 100.0)
            return round(self.price * discount_factor, 2)
        return self.price
    @property
    def total_stock(self):
        if not self.variations:
            return 0
        return sum(var.stock for var in self.variations)
    def __str__(self):
        return self.name

class Variation(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.stock} unid.)"

product_section_association = db.Table('product_section_association',
    db.metadata, 
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('product_section.id'))
)

class ProductSection(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Destaques")
    products = db.relationship('Product', secondary=product_section_association,
                               backref=db.backref('sections', lazy='dynamic'))
    def __str__(self): return self.title

class TextSection(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, default='sobre-nos')
    title = db.Column(db.String(150), nullable=False, default="Sobre Nós")
    content = db.Column(db.Text, nullable=True)
    def __str__(self): return self.title

# --- MODELO FOOTERLINK ATUALIZADO ---
class FooterLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    column = db.Column(db.Integer, default=1)
    
    # --- 1. ADICIONE ESTA NOVA PROPRIEDADE ---
    @property
    def final_url(self):
        """
        Formata a URL para garantir que links externos funcionem.
        """
        if not self.url or self.url == "#":
            return "#"
        
        # Se o usuário já digitou http:// or https://, respeite
        if self.url.startswith('http://') or self.url.startswith('https://'):
            return self.url
        
        # Se for um link de email (mailto:) ou telefone (tel:), respeite
        if self.url.startswith('mailto:') or self.url.startswith('tel:'):
            return self.url
        
        # Para links externos como 'www.google.com' ou 'instagram.com'
        return f"//{self.url}"
    # --- FIM DA PROPRIEDADE ---

    def __str__(self): return f"{self.title} (Coluna {self.column})"
# --- FIM DA ATUALIZAÇÃO ---

class OrderItem(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('variation.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)
    order = relationship('Order', back_populates='order_items')
    variation = relationship('Variation')
    def __str__(self):
        return f"{self.quantity}x {self.variation.product.name} ({self.variation.size})"

class Order(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    total_price = db.Column(db.Float, nullable=False)
    whatsapp_url = db.Column(db.String(1000), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='Pendente')
    restocked = db.Column(db.Boolean, default=False)
    order_items = relationship('OrderItem', back_populates='order', lazy='dynamic', cascade='all, delete-orphan')
    @property
    def items_summary(self):
        if not self.order_items:
            return "N/A"
        return ", ".join([f"{item.quantity}x {item.variation.product.name} ({item.variation.size})" for item in self.order_items])
    def __str__(self):
        return f"Pedido #{self.id} - R${self.total_price:.2f} ({self.status})"

class SiteStat(db.Model):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Integer, default=0)
    def __str__(self):
        return f"{self.key}: {self.value}"

class User(db.Model, UserMixin):
    # ... (Sem alteração) ...
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    def __str__(self):
        return self.email
