# admin.py
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from flask_admin.form.upload import ImageUploadField
from flask_admin.menu import MenuLink
# Importar ValidationError e flash
from wtforms.validators import ValidationError
from flask import flash


from extensions import db
from models import (
    HeaderCategory, CircularCategory, Banner,
    Product, ProductSection, TextSection, FooterLink
)

# --- Configuração do Caminho de Upload ---
basedir = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(basedir, 'static', 'uploads')


# --- Views de Admin Personalizadas ---

class SecureModelView(ModelView):
    # Classe base segura
    pass

class HeaderCategoryView(SecureModelView):
    # Configurações padrão, sem traduções
    form_columns = ('name', 'url', 'order')
    column_list = ('name', 'url', 'order')
    column_default_sort = ('order', False) # Ordena por 'order' na lista

class ProductView(SecureModelView):
    form_overrides = {
        'image_url': ImageUploadField
    }
    form_args = {
        'image_url': {
            'label': 'Imagem do Produto',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'product_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif'),
        }
    }
    column_list = ('name', 'price', 'image_url', 'slug')
    form_columns = ('name', 'price', 'image_url', 'slug', 'sections')
    column_searchable_list = ('name',) # Permite buscar por nome
    column_filters = ('sections',) # Permite filtrar por seção

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
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif'),
        },
        'image_url_mobile': {
            'label': 'Imagem Mobile (opcional) (600x600)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'banner_m_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif'),
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
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif'),
        }
    }
    column_list = ('name', 'image_url', 'section', 'order')
    form_columns = ('name', 'image_url', 'link_url', 'section', 'order')
    column_default_sort = ('order', False)
    column_filters = ('section',) # Filtro por seção 1 ou 2

class TextSectionView(SecureModelView):
    form_overrides = {
        'content': CKEditorField
    }
    form_columns = ('key', 'title', 'content')
    column_list = ('key', 'title')
    # Impede criar/deletar novas seções de texto (geralmente só 'sobre-nos')
    can_create = False
    can_delete = False

class ProductSectionView(SecureModelView):
    # Configurações básicas sem tradução
    column_list = ('title',)
    form_columns = ('title', 'products')

    # Adiciona descrição clara no formulário usando form_args
    form_args = dict(
        products=dict(
            label='Produtos nesta seção',
            description='Selecione no máximo 4 produtos.' # Texto de ajuda abaixo do campo
        ),
        title=dict(
            label='Título da Seção (ex: Destaques)'
        )
    )

    def on_model_change(self, form, model, is_created):
        """
        Chamado ANTES de salvar. Verifica a quantidade de produtos.
        """
        if hasattr(form, 'products') and form.products.data:
            selected_products_count = len(form.products.data)
            if selected_products_count > 4:
                # Mensagem flash clara no topo
                flash(f'ERRO AO SALVAR: Você selecionou {selected_products_count} produtos. O máximo permitido por seção é 4. Por favor, remova o(s) excedente(s).', 'error')
                # Impede o salvamento e marca o campo
                raise ValidationError('Limite de 4 produtos por seção excedido.')
        # Continua se a validação passar
        super().on_model_change(form, model, is_created)


class FooterLinkView(SecureModelView):
     # Configurações padrão, sem traduções
    form_columns = ('title', 'url', 'order', 'column')
    column_list = ('title', 'url', 'column', 'order')
    column_default_sort = ('column', False)
    column_filters = ('column',) # Filtro por coluna (1, 2, 3...)

def init_admin(app):
    """Inicializa o Flask-Admin."""
    admin = Admin(app, name='Obá Moda Afro - Dashboard', url='/admin')

    # Adiciona as views usando as classes apropriadas e os ícones
    # Os nomes aqui ("Categorias (Header)") são usados no menu
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

    # Adiciona um link para "Voltar ao site"
    admin.add_link(MenuLink(name='Voltar ao Site', category='', url='/',
                   icon_value='fa-home'))