# admin.py
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from flask_admin.form.upload import ImageUploadField
from flask_admin.menu import MenuLink
from wtforms.validators import ValidationError
from flask import flash

from slugify import slugify

from extensions import db
from models import (
    HeaderCategory, CircularCategory, Banner,
    Product, ProductSection, TextSection, FooterLink,
    Variation
)

# --- Configuração do Caminho de Upload ---
basedir = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(basedir, 'static', 'uploads')


# --- Views de Admin Personalizadas ---

class SecureModelView(ModelView):
    # Classe base segura
    pass

class HeaderCategoryView(SecureModelView):
    form_columns = ('name', 'url', 'order')
    column_list = ('name', 'url', 'order')
    column_default_sort = ('order', False)

# --- CLASSE VariationView REMOVIDA (era desnecessária) ---

class ProductView(SecureModelView):
    form_overrides = {
        'image': ImageUploadField,
        'description': CKEditorField
    }
    
    form_args = {
        'image': {
            'label': 'Imagem do Produto',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'product_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'description': {
            'label': 'Descrição Completa'
        },
        'slug': {
            'label': 'URL (slug)',
            'description': 'Deixe em branco para gerar automaticamente a partir do nome.'
        }
    }
    
    column_list = ('name', 'price', 'image', 'active', 'total_stock', 'slug')
    form_columns = ('name', 'description', 'price', 'image', 'active', 'slug', 'sections')
    
    column_searchable_list = ('name',) 
    column_filters = ('sections', 'active')

    # --- AQUI ESTÁ A CORREÇÃO ---
    inline_models = [(Variation, {
        'form_label': 'Variação',
        'form_columns': ['id', 'size', 'stock'], # <-- 1. ADICIONADO 'id' AQUI
        'min_entries': 1,
    })]

    def on_model_change(self, form, model, is_created):
        if not model.slug:
            model.slug = slugify(model.name)
        
        check_slug = Product.query.filter_by(slug=model.slug).first()
        if check_slug and check_slug.id != model.id:
            model.slug = f"{model.slug}-{model.id or 'novo'}"
            flash(f'O slug foi alterado para "{model.slug}" pois o original já existia.', 'warning')
            
        super().on_model_change(form, model, is_created)


class BannerView(SecureModelView):
    # ... (sem alterações) ...
    form_overrides = {
        'image_url_desktop': ImageUploadField,
        'image_url_mobile': ImageUploadField,
    }
    form_args = {
        'image_url_desktop': {
            'label': 'Imagem Desktop (1920x600)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'banner_d_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'image_url_mobile': {
            'label': 'Imagem Mobile (opcional) (600x600)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'banner_m_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        }
    }
    column_list = ('title', 'image_url_desktop', 'link_url', 'order')
    form_columns = ('title', 'subtitle', 'image_url_desktop', 'image_url_mobile', 'link_url', 'order')
    column_default_sort = ('order', False)

class CircularCategoryView(SecureModelView):
    # ... (sem alterações) ...
    form_overrides = {
        'image_url': ImageUploadField
    }
    form_args = {
        'image_url': {
            'label': 'Imagem (100x100)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'cat_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        }
    }
    column_list = ('name', 'image_url', 'section', 'order')
    form_columns = ('name', 'image_url', 'link_url', 'section', 'order')
    column_default_sort = ('order', False)
    column_filters = ('section',) 

class TextSectionView(SecureModelView):
    # ... (sem alterações) ...
    form_overrides = {
        'content': CKEditorField
    }
    form_columns = ('key', 'title', 'content')
    column_list = ('key', 'title')
    can_create = False
    can_delete = False

class ProductSectionView(SecureModelView):
    # ... (sem alterações) ...
    column_list = ('title',)
    form_columns = ('title', 'products')
    form_args = dict(
        products=dict(
            label='Produtos nesta seção',
            description='Selecione no máximo 4 produtos.' 
        ),
        title=dict(
            label='Título da Seção (ex: Destaques)'
        )
    )

    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'products') and form.products.data:
            selected_products_count = len(form.products.data)
            if selected_products_count > 4:
                flash(f'ERRO AO SALVAR: Você selecionou {selected_products_count} produtos. O máximo permitido por seção é 4. Por favor, remova o(s) excedente(s).', 'error')
                raise ValidationError('Limite de 4 produtos por seção excedido.')
        super().on_model_change(form, model, is_created)

class FooterLinkView(SecureModelView):
    # ... (sem alterações) ...
    form_columns = ('title', 'url', 'order', 'column')
    column_list = ('title', 'url', 'column', 'order')
    column_default_sort = ('column', False)
    column_filters = ('column',)

def init_admin(app):
    """Inicializa o Flask-Admin."""
    admin = Admin(app, name='Obá Moda Afro - Dashboard', url='/admin')

    # Adiciona as views (sem alterações)
    admin.add_view(HeaderCategoryView(HeaderCategory, db.session, name='Categorias (Header)',
                   menu_icon_value='fa-list-alt'))
    admin.add_view(CircularCategoryView(CircularCategory, db.session, name='Categorias (Bolinhas)',
                   menu_icon_value='fa-dot-circle-o'))
    admin.add_view(BannerView(Banner, db.session, name='Banners Carrossel',
                   menu_icon_value='fa-image'))
                   
    admin.add_view(ProductView(Product, db.session, name='Produtos',
                   menu_icon_value='fa-tags'))
                   
    admin.add_view(ProductSectionView(ProductSection, db.session, name='Seções de Produto',
                   menu_icon_value='fa-folder-open'))
    admin.add_view(TextSectionView(TextSection, db.session, name='Seções de Texto',
                   menu_icon_value='fa-file-text-alt'))
    admin.add_view(FooterLinkView(FooterLink, db.session, name='Links (Rodapé)',
                   menu_icon_value='fa-link'))

    admin.add_link(MenuLink(name='Voltar ao Site', category='', url='/',
                   icon_value='fa-home'))