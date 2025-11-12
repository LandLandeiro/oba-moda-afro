# admin.py
import os
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_admin import Admin, AdminIndexView, expose 
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from flask_admin.form.upload import ImageUploadField
from flask_admin.menu import MenuLink
from wtforms.validators import ValidationError
from flask import flash, redirect, url_for, request, render_template
from flask_login import current_user, logout_user 
from slugify import slugify
from wtforms.fields import DateField

from flask_admin.actions import action
from slugify import slugify

from extensions import db
from models import (
    HeaderCategory, CircularCategory, Banner,
    Product, ProductSection, TextSection,
    Variation, Category,
    FooterLink,
    Product, Promotion,
    Order, SiteStat,
    OrderItem
)

# --- Configuração do Caminho de Upload ---
basedir = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(basedir, 'static', 'uploads')


# --- Views de Admin Personalizadas ---

class SecureModelView(ModelView):
    
    def is_accessible(self):
        # Retorna True se o usuário estiver logado
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

class SecureAdminIndexView(AdminIndexView):
    """
    Protege a página inicial do painel admin e exibe o dashboard com filtros.
    """
    
    def __init__(self, template=None, url=None, **kwargs):
        super(SecureAdminIndexView, self).__init__(
            template=template or 'admin/index.html', # Nosso template de dashboard
            url=url or '/admin',
            **kwargs
        )

    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self, **kwargs):
        """
        Carrega a página de dashboard com os dados para os gráficos,
        processando os filtros de data.
        """
        
        # --- 1. ESTA É A CORREÇÃO CRÍTICA ---
        # Carrega os args padrão do admin (incluindo 'admin_base_template')
        template_args = self._template_args.copy()
        
        # --- 2. PROCESSAR FILTROS DE DATA ---
        try:
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')

            if not end_date_str:
                end_date = datetime.now()
                end_date_str = end_date.strftime('%Y-%m-%d')
            else:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

            if not start_date_str:
                start_date = end_date - timedelta(days=30)
                start_date_str = start_date.strftime('%Y-%m-%d')
            else:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        except ValueError:
            flash('Formato de data inválido. Usando o padrão (últimos 30 dias).', 'warning')
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            end_date_str = end_date.strftime('%Y-%m-%d')
            start_date_str = start_date.strftime('%Y-%m-%d')

        
        # --- 3. QUERIES (DENTRO DE UM 'TRY' CORRIGIDO) ---
        try:
            # Cria uma consulta base de pedidos dentro do período
            base_query_pedidos = Order.query.filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
            
            total_leads = base_query_pedidos.count()

            vendas_concluidas_query = base_query_pedidos.filter(Order.status == 'Concluído')
            total_vendas_concluidas = vendas_concluidas_query.count()

            receita_total_raw = db.session.query(func.sum(Order.total_price))\
                                  .filter(Order.status == 'Concluído')\
                                  .filter(Order.created_at >= start_date, Order.created_at <= end_date)\
                                  .scalar()
            receita_total = receita_total_raw or 0.0

            taxa_conversao = 0.0
            if total_leads > 0:
                taxa_conversao = (total_vendas_concluidas / total_leads) * 100

            # 4. DADOS PARA GRÁFICOS
            status_data = db.session.query(Order.status, func.count(Order.id))\
                              .filter(Order.created_at >= start_date, Order.created_at <= end_date)\
                              .group_by(Order.status).all()
            dados_status_pizza = {
                'labels': [s[0] for s in status_data],
                'data': [s[1] for s in status_data]
            }

            receita_por_dia_raw = db.session.query(
                                    func.date(Order.created_at), 
                                    func.sum(Order.total_price)
                                 ).filter(
                                    Order.status == 'Concluído',
                                    Order.created_at >= start_date,
                                    Order.created_at <= end_date
                                 ).group_by(
                                    func.date(Order.created_at)
                                 ).order_by(
                                    func.date(Order.created_at)
                                 ).all()
            
            dados_receita_linha = {
                'labels': [ (datetime.strptime(d[0], '%Y-%m-%d') if isinstance(d[0], str) else d[0]).strftime('%d/%m') for d in receita_por_dia_raw ],
                'data': [float(d[1]) for d in receita_por_dia_raw]
            }
            
            # --- CÓDIGO REMOVIDO ---
            # O gráfico 'top_produtos' foi removido do template, 
            # então não precisamos mais calcular isso.
            # --- FIM DA REMOÇÃO ---

            # --- LÓGICA DE GESTÃO DE ESTOQUE ---
            LOW_STOCK_THRESHOLD = 5
            
            all_active_products = Product.query.filter_by(active=True).all()
            
            low_stock_products = [
                p for p in all_active_products
                if p.total_stock > 0 and p.total_stock <= LOW_STOCK_THRESHOLD
            ]
            
            out_of_stock_products_inactive = Product.query.filter_by(active=False).all()
            out_of_stock_products_active = [
                p for p in all_active_products
                if p.total_stock == 0
            ]
            
            out_of_stock_products = out_of_stock_products_active + out_of_stock_products_inactive
            
            low_stock_count = len(low_stock_products)
            out_of_stock_count = len(out_of_stock_products)
            
            url_filtro_esgotados = url_for('product.index_view') + '?flt2_0=False'
            # --- FIM DA LÓGICA DE ESTOQUE ---

            # 5. ENVIAR DADOS PARA O TEMPLATE 
            template_args.update({
                'start_date_str': start_date_str,
                'end_date_str': end_date_str,
                'receita_total': receita_total,
                'total_leads': total_leads,
                'total_vendas_concluidas': total_vendas_concluidas,
                'taxa_conversao': taxa_conversao,
                'dados_status_pizza': dados_status_pizza,
                'dados_receita_linha': dados_receita_linha,
                # 'dados_produtos_carrinho' removido
                
                'low_stock_count': low_stock_count,
                'out_of_stock_count': out_of_stock_count,
                'low_stock_products': sorted(low_stock_products, key=lambda p: p.total_stock), 
                'out_of_stock_products': sorted(out_of_stock_products, key=lambda p: p.name), 
                'url_filtro_esgotados': url_filtro_esgotados 
            })

        # --- 6. 'EXCEPT' CORRIGIDO E PAREADO ---
        except Exception as e:
            # Mostra o erro real no log do console (ajuda a debugar)
            print(f"!!!!!!!!!! ERRO AO CARREGAR O DASHBOARD: {e} !!!!!!!!!!")
            
            flash(f'Erro ao carregar o dashboard: {e}', 'danger')
            template_args.update({
                'start_date_str': start_date_str, 'end_date_str': end_date_str,
                'receita_total': receita_total, # Os KPIs (calculados antes) ainda podem aparecer
                'total_leads': total_leads,
                'total_vendas_concluidas': total_vendas_concluidas,
                'taxa_conversao': taxa_conversao,
                'dados_status_pizza': {'labels': [], 'data': []}, # Gráficos são zerados
                'dados_receita_linha': {'labels': [], 'data': []},
                
                'low_stock_count': 0,
                'out_of_stock_count': 0,
                'low_stock_products': [],
                'out_of_stock_products': [], 
                'url_filtro_esgotados': url_for('product.index_view') 
            })
        
        # --- 7. RENDERIZAR NO FINAL ---
        return self.render(
            self._template,
            **template_args
        )

# ... (O resto do arquivo: CategoryView, ProductView, etc. permanece igual) ...

class HeaderCategoryView(SecureModelView):
    form_columns = ('name', 'category', 'order')
    column_list = ('name', 'category', 'order')
    column_default_sort = ('order', False)

    form_args = {
        'category': {
            'label': 'Link da Categoria',
            'description': 'Selecione a categoria de produto para a qual este link deve apontar.'
        }
    }   

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
        },
        
        'price': {
            'label': 'Preço Normal (Cheio)'
        }
    }
    
    column_list = ('name', 'categories', 'price',  'image', 'active', 'total_stock', 'view_count', 'cart_add_count', 'slug')
    form_columns = ('name', 'categories', 'description', 'price',  'image', 'active', 'slug', 'sections')
    
    column_searchable_list = ('name',) 
    # A ordem aqui é crucial: [0]categories, [1]sections, [2]active
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

class PromotionView(SecureModelView):
    # Colunas que você vê na lista
    column_list = ('name', 'is_active', 'start_date', 'end_date', 'discount_percent', 'products')
    
    # Campos que você preenche no formulário
    form_columns = ('name', 'is_active', 'start_date', 'end_date', 'discount_percent', 'products')
    
    # Isso faz os campos de data usarem um seletor de calendário
    form_overrides = {
        'start_date': DateField,
        'end_date': DateField
    }
    
    form_args = {
        'name': {'label': 'Nome da Campanha (Ex: Black Friday)'},
        'is_active': {'label': 'Ativar esta promoção?'},
        'start_date': {'label': 'Data de Início (Opcional)', 'description': 'Deixe em branco para começar imediatamente.'},
        'end_date': {'label': 'Data de Fim (Opcional)', 'description': 'Deixe em branco para nunca expirar.'},
        'discount_percent': {'label': 'Desconto (%)', 'description': 'Ex: digite 15 para 15% de desconto.'},
        'products': {'label': 'Produtos nesta Promoção', 'description': 'Selecione os produtos que farão parte desta campanha.'}
    }

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
        },
        'link_url': {
            'label': 'URL Externa (Opcional)',
            'description': 'Preencha este campo APENAS se o banner for para um site externo.'
        },
        'product': {
            'label': 'Link para Produto (Opcional)',
            'description': 'Selecione um produto da loja para o banner linkar diretamente para ele.'
        }
    }
    column_list = ('title', 'image_url_desktop','product', 'link_url', 'order')
    form_columns = ('title', 'subtitle', 'image_url_desktop', 'image_url_mobile', 'link_url', 'product', 'order')
    column_default_sort = ('order', False)

class FooterLinkView(SecureModelView):
    form_columns = ('title', 'url', 'order', 'column')
    column_list = ('title', 'url', 'order', 'column')
    column_default_sort = ('column', False)
    column_filters = ('column',)

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
        },
        'category': {
            'label': 'Link da Categoria',
            'description': 'Selecione a categoria de produto para a qual esta bolinha deve apontar.'
        }
    }
    
    column_list = ('name', 'image_url', 'category', 'section', 'order')
    form_columns = ('name', 'image_url', 'category', 'section', 'order')
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
        # Esta é a ÚNICA verificação que deve estar aqui
        if hasattr(form, 'products') and form.products.data:
            selected_products_count = len(form.products.data)
            if selected_products_count > 4:
                flash(f'ERRO AO SALVAR: Você selecionou {selected_products_count} produtos. O máximo permitido por seção é 4. Por favor, remova o(s) excedente(s).', 'error')
                raise ValidationError('Limite de 4 produtos por seção excedido.')
        
        # O 'super()' deve ser chamado apenas uma vez, no final.
        super().on_model_change(form, model, is_created)

# --- NOVO: OrderItemView (Apenas para o admin) ---
class OrderItemView(SecureModelView):
    """Visualização para os Itens do Pedido (apenas leitura)"""
    can_create = False
    can_edit = False
    can_delete = False
    
    column_list = ['order', 'variation', 'quantity', 'price_per_item']


# --- ATUALIZADO: OrderView (Com lógica de restock) ---
class OrderView(SecureModelView):
    """Visualização para os Pedidos/Leads"""
    can_create = True # criar pedidos manualmente
    can_edit = True
    can_delete = True

    form_choices = {
        'status': [
            ('Pendente', 'Pendente'),
            ('Concluído', 'Concluído'),
            ('Cancelado', 'Cancelado')
        ]
    }

    # Mostra os itens do pedido direto na página de edição
    inline_models = (OrderItemView(OrderItem, db.session, name="Itens do Pedido"),)

    column_editable_list = ['status']
    
    # 'items_summary' agora é uma @property, funciona na lista!
    column_list = ('id', 'status','created_at', 'total_price', 'items_summary', 'restocked', 'whatsapp_url')
    
    # 'restocked' não deve ser editável no formulário principal
    form_columns = ('status', 'created_at', 'total_price', 'whatsapp_url')
    
    column_default_sort = ('created_at', True) # Ordenar por mais novo
    column_searchable_list = ('order_items.variation.product.name',) # Permite buscar pelo nome do produto
    column_filters = ('created_at', 'total_price', 'status', 'restocked')

    def on_model_change(self, form, model, is_created):
        """
        Esta é a lógica de RESTOCK.
        É acionada sempre que um Pedido é salvo no admin.
        """
        if not is_created and 'status' in form.data:
            
            # --- LÓGICA DE CANCELAMENTO ---
            # Se o novo status é 'Cancelado' E o estoque ainda não foi devolvido
            if model.status == 'Cancelado' and not model.restocked:
                try:
                    for item in model.order_items:
                        if item.variation:
                            item.variation.stock += item.quantity
                            db.session.add(item.variation)
                            flash(f"Estoque devolvido: {item.quantity}x {item.variation.product.name} ({item.variation.size})", "success")
                    
                    # Marca que o estoque deste pedido foi devolvido
                    model.restocked = True
                    
                except Exception as e:
                    flash(f"Erro ao devolver o estoque: {e}", "danger")

            # --- LÓGICA DE RE-SUBTRAÇÃO (Opcional, mas seguro) ---
            # Se o status MUDOU DE 'Cancelado' para outra coisa (ex: Pendente)
            # E o estoque JÁ TINHA SIDO devolvido
            elif model.status != 'Cancelado' and model.restocked:
                try:
                    # Checa se há estoque ANTES de subtrair de novo
                    for item in model.order_items:
                        if item.variation and item.variation.stock < item.quantity:
                            flash(f"Não foi possível re-subtrair estoque para {item.variation.product.name}. Estoque insuficiente.", "error")
                            # Impede a mudança de status
                            model.status = 'Cancelado' 
                            return super().on_model_change(form, model, is_created)

                    # Se todos os itens têm estoque, subtrai
                    for item in model.order_items:
                        if item.variation:
                            item.variation.stock -= item.quantity
                            db.session.add(item.variation)
                            flash(f"Estoque re-subtraído: {item.quantity}x {item.variation.product.name} ({item.variation.size})", "warning")
                    
                    # Marca que o estoque não está mais devolvido
                    model.restocked = False

                except Exception as e:
                    flash(f"Erro ao re-subtrair o estoque: {e}", "danger")

        super().on_model_change(form, model, is_created)


class SiteStatView(SecureModelView):
    """Visualização para as Estatísticas"""
    can_create = False # Não criar novas chaves
    can_delete = False # Não deletar chaves
    
    # Permite editar o valor (ex: para zerar um contador)
    can_edit = True 
    
    column_list = ('key', 'value')


def init_admin(app):
    """Inicializa o Flask-Admin."""
    admin = Admin(
        app, 
        name='Obá Moda Afro - Dashboard', 
        url='/admin',
        index_view=SecureAdminIndexView() # <-- Define a view de index segura
        
    )

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
    admin.add_view(FooterLinkView(FooterLink, db.session, name='Links (Rodapé)',
                   menu_icon_value='fa-link'))
    
    # ATUALIZADO: Agrupando os Pedidos
    admin.add_view(OrderView(Order, db.session, name='Pedidos (Leads)',
                   category='Vendas', menu_icon_value='fa-money'))
    admin.add_view(OrderItemView(OrderItem, db.session, name='Itens dos Pedidos',
                   category='Vendas', menu_icon_value='fa-shopping-basket'))
    
    admin.add_view(SiteStatView(SiteStat, db.session, name='Estatísticas',
                   menu_icon_value='fa-bar-chart'))
    admin.add_view(PromotionView(Promotion, db.session, name='Promoções (Campanhas)',
                   menu_icon_value='fa-bullhorn'))
    admin.add_link(MenuLink(name='Voltar ao Site', category='', url='/',
                   icon_value='fa-home'))
