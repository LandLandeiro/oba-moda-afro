# admin.py
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from flask_admin.form.upload import ImageUploadField
from flask_admin.menu import MenuLink
from wtforms.validators import ValidationError
from flask import flash

from flask_admin.actions import action
from slugify import slugify

from extensions import db
from models import (
    HeaderCategory, CircularCategory, Banner,
    Product, ProductSection, TextSection,
    Variation, Category
)

# --- Configuração do Caminho de Upload ---
basedir = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(basedir, 'static', 'uploads')


# --- Views de Admin Personalizadas ---

class SecureModelView(ModelView):
    pass

class HeaderCategoryView(SecureModelView):
    form_columns = ('name', 'url', 'order')
    column_list = ('name', 'url', 'order')
    column_default_sort = ('order', False)

class CategoryView(SecureModelView):
    form_columns = ('name', 'description', 'products')
    column_list = ('name', 'slug', 'products')
    
    form_args = {
         'products': {
            'label': 'Produtos nesta Categoria'
         }
    }

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(model.name)
        check_slug = Category.query.filter_by(slug=model.slug).first()
        if check_slug and check_slug.id != model.id:
            model.slug = f"{model.slug}-{model.id or 'novo'}"
            flash(f'O slug foi alterado para "{model.slug}" pois o original já existia.', 'warning')
        super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        if model.products:
            flash(f'Não é possível excluir a categoria "{model.name}", pois ela contém produtos. Mova os produtos para outra categoria primeiro.', 'error')
            raise ValidationError("Categoria não está vazia.")
        super().on_model_delete(model)

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
        },
        'categories': {
            'label': 'Categorias',
            'description': 'Selecione uma ou mais categorias para o produto.'
        }
    }
    
    column_list = ('name', 'categories', 'price', 'image', 'active', 'total_stock', 'slug')
    form_columns = ('name', 'categories', 'description', 'price', 'image', 'active', 'slug', 'sections')
    
    column_searchable_list = ('name',) 
    column_filters = ('categories', 'sections', 'active')

    inline_models = [(Variation, {
        'form_label': 'Variação',
        'form_columns': ['id', 'size', 'stock'],
        'min_entries': 1,
    })]

    def on_model_change(self, form, model, is_created):
        if form.slug.data:
            model.slug = slugify(form.slug.data)
        else:
            model.slug = slugify(model.name)
        query = self.model.query.filter_by(slug=model.slug)
        if model.id:
            query = query.filter(self.model.id != model.id)
        check_slug = query.first()
        if check_slug:
            unique_suffix = model.id or 'novo' 
            model.slug = f"{model.slug}-{unique_suffix}"
            flash(f'O slug foi alterado para "{model.slug}" pois o original já existia.', 'warning')
        super().on_model_change(form, model, is_created)

    @action('duplicate', 'Duplicar', 'Tem certeza que deseja duplicar os produtos selecionados?')
    def action_duplicate(self, ids):
        try:
            product_query = self.model.query.filter(self.model.id.in_(ids))
            
            for product in product_query.all():
                new_name = f"{product.name} (Cópia)"
                new_slug = slugify(new_name)
                
                check_slug = self.model.query.filter_by(slug=new_slug).first()
                if check_slug:
                    new_slug = f"{new_slug}-{product.id}"

                new_product = self.model(
                    name=new_name,
                    slug=new_slug,
                    description=product.description,
                    price=product.price,
                    image=product.image,
                    active=False 
                )
                new_product.categories = list(product.categories)
                new_product.sections = list(product.sections)
                new_vars = []
                for var in product.variations:
                    new_var = Variation(
                        size=var.size,
                        stock=var.stock
                    )
                    new_vars.append(new_var)
                
                new_product.variations = new_vars
                self.session.add(new_product)
            
            self.session.commit()
            flash(f"{len(ids)} produto(s) duplicado(s) com sucesso. Lembre-se de ativá-los após a edição.", 'success')
        
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(f"Falha ao duplicar produtos: {ex}", 'error')

class BannerView(SecureModelView):
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
    form_overrides = {
        'content': CKEditorField
    }
    form_columns = ('key', 'title', 'content')
    column_list = ('key', 'title')
    can_create = True
    can_delete = True

class ProductSectionView(SecureModelView):
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


def init_admin(app):
    """Inicializa o Flask-Admin."""
    admin = Admin(app, name='Obá Moda Afro - Dashboard', url='/admin')

    admin.add_view(CategoryView(Category, db.session, name='Categorias',
                   menu_icon_value='fa-bookmark'))
    admin.add_view(ProductView(Product, db.session, name='Produtos',
                   menu_icon_value='fa-tags'))
    admin.add_view(HeaderCategoryView(HeaderCategory, db.session, name='Categorias (Header)',
                   menu_icon_value='fa-list-alt'))
    admin.add_view(CircularCategoryView(CircularCategory, db.session, name='Categorias (Bolinhas)',
                   menu_icon_value='fa-dot-circle-o'))
    admin.add_view(BannerView(Banner, db.session, name='Banners (Carrossel)',
                   menu_icon_value='fa-image'))
    admin.add_view(ProductSectionView(ProductSection, db.session, name='Seções de Produto',
                   menu_icon_value='fa-folder-open'))
    admin.add_view(TextSectionView(TextSection, db.session, name='Seções de Texto',
                   menu_icon_value='fa-file-text-alt'))

    admin.add_link(MenuLink(name='Voltar ao Site', category='', url='/',
                   icon_value='fa-home'))