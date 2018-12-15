from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import ContextMixin

from borgia.mixins import LateralMenuBaseMixin
from borgia.utils import (get_permission_name_group_managing,
                          group_name_display, is_association_manager,
                          simple_lateral_link)
from shops.models import Product, Shop
from shops.utils import is_shop_manager


class ShopPermissionAndContextMixin(PermissionRequiredMixin, ContextMixin):
    """
    Mixin for Shop and Product views.
    For Permission :
    This mixin check if the user has the permission required. Then, it check if the user is a association manager.
    If the user is indeed an association manager, he can access forms for other shops.
    If the user is "only" a shop manager, he is restricted to his own shop and the related products.

    Also, add to context a few variable :
    - is_association_manager, bool
    - shop, Shop object
    """
    permission_required = None

    def __init__(self):
        self.shop = None
        self.is_association_manager = None

    def add_shop_object(self):
        """
        Define shop object.
        Raise Http404 is shop doesn't exist.
        """
        try:
            self.shop = Shop.objects.get(pk=self.kwargs['shop_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        self.add_shop_object()

    def has_permission(self):
        self.add_context_objects()
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            if is_association_manager(self.request.user):
                self.is_association_manager = True
                return True
            else:
                self.is_association_manager = False
                return is_shop_manager(self.shop, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['is_association_manager'] = self.is_association_manager
        return context


class ProductPermissionAndContextMixin(ShopPermissionAndContextMixin):
    """
    Mixin for Product views.
    This mixin inherite from ShopPermissionAndContextMixin, and keep Permission verification.
    It only add the product context.
    """

    def __init__(self):
        self.product = None

    def add_product_object(self):
        try:
            self.product = Product.objects.get(pk=self.kwargs['product_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_context_objects(self):
        super().add_context_objects()
        self.add_product_object()

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            return self.product.shop == self.shop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


class LateralMenuShopsMixin(LateralMenuBaseMixin):
    """
    Lateral Menu for shops managers.

    Add :
    - Home page shops
    - Checkup
    - OperatorSale module
    - Sales
    - Products
    - StockEntries
    - Inventories
    - OperatorSale Configuration
    - SelfSale Configuration
    - Shop groups management
    """

    def lateral_menu(self):
        nav_tree = super().lateral_menu()
        user = self.request.user
        shop = self.shop

        nav_tree.append(
            simple_lateral_link(
                'Accueil Magasin ' + shop.name.title(),
                'briefcase',
                'lm_workboard',
                reverse('url_shop_workboard', 
                        kwargs={'shop_pk': shop.pk})
            ))

        if user.has_perm('shops.view_shop'):
            nav_tree.append(
                simple_lateral_link(
                    'Checkup',
                    'user',
                    'lm_shop_checkup',
                    reverse('url_shop_checkup',
                            kwargs={'shop_pk': shop.pk})
                ))

        # OperatorSale Module
        if shop.modules_operatorsalemodule_shop.first() is not None:
            if shop.modules_operatorsalemodule_shop.first().state is True:
                if user.has_perm('modules.use_operatorsalemodule'):
                    nav_tree.append(simple_lateral_link(
                        label='Module vente',
                        fa_icon='shopping-basket',
                        id_link='lm_operatorsale_interface_module',
                        url=reverse(
                            'url_shop_module_sale',
                            kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
                        )
                    )

        # Sales
        if user.has_perm('finances.view_sale'):
            nav_tree.append(
                simple_lateral_link(
                    'Ventes',
                    'shopping-cart',
                    'lm_sale_list',
                    reverse(
                        'url_sale_list', 
                        kwargs={'shop_pk': shop.pk})
                )
            )

        # Products
        if user.has_perm('shops.view_product'):
            nav_tree.append(
                simple_lateral_link(
                    label='Produits',
                    fa_icon='cube',
                    id_link='lm_product_list',
                    url=reverse(
                        'url_product_list',
                        kwargs={'shop_pk': shop.pk})
                )
            )

        # StockEntries
        if user.has_perm('stocks.view_stockentry'):
            nav_tree.append(
                simple_lateral_link(
                    'Entrées de stock',
                    'list',
                    'lm_stockentry_list',
                    reverse(
                        'url_stockentry_list', 
                        kwargs={'shop_pk': shop.pk})
                )
            )
        
        # Inventories
        if user.has_perm('stocks.view_stockentry'):
            nav_tree.append(
                simple_lateral_link(
                    'Entrées de stock',
                    'list',
                    'lm_inventory_list',
                    reverse(
                        'url_inventory_list', 
                        kwargs={'shop_pk': shop.pk})
                )
            )

        if user.has_perm('modules.view_config_selfsalemodule'):
            nav_tree.append(
                simple_lateral_link(
                    label='Configuration vente libre service',
                    fa_icon='shopping-basket',
                    id_link='lm_selfsale_module',
                    url=reverse('url_shop_module_config',
                                kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}
                                )
                ))

        if user.has_perm('modules.view_config_operatorsalemodule'):
            nav_tree.append(
                simple_lateral_link(
                    label='Configuration vente par opérateur',
                    fa_icon='coffee',
                    id_link='lm_operatorsale_module',
                    url=reverse('url_shop_module_config',
                                kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'}
                                )
                ))

        # Groups management
        nav_management_groups = {
            'label': 'Gestion groupes magasin',
            'icon': 'users',
            'id': 'lm_group_management',
            'subs': []
        }
        groups = [Group.objects.get(name='chiefs-'+shop.name), Group.objects.get(name='associates-'+shop.name)]
        for group in groups:
            if user.has_perm(get_permission_name_group_managing(group)):
                nav_management_groups['subs'].append(
                        simple_lateral_link(
                        'Gestion ' + group_name_display(group),
                        'users',
                        'lm_group_manage_' + group.name,
                        reverse('url_group_update', kwargs={
                            'pk': group.pk})
                    ))

        nav_tree.append(nav_management_groups)



        if self.lm_active is not None:
            for link in nav_tree:
                try:
                    for sub in link['subs']:
                        if sub['id'] == self.lm_active:
                            sub['active'] = True
                            break
                except KeyError:
                    if link['id'] == self.lm_active:
                        link['active'] = True
                        break
        return nav_tree


class ShopMixin(ShopPermissionAndContextMixin, LateralMenuShopsMixin):
    """
    Mixin that check permission, give context for shops and add SHOPS lateral menu.
    """


class ProductMixin(ProductPermissionAndContextMixin, LateralMenuShopsMixin):
    """
    Mixin that check permission, give context for products and add SHOPS lateral menu.

    """
