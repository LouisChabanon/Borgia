from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from shops.models import Product, Shop
from shops.utils import DEFAULT_PERMISSIONS_CHIEFS
from borgia.tests.tests_views import BaseBorgiaViewsTestCase


class BaseShopsViewsTest(BaseBorgiaViewsTestCase):
    def setUp(self):
        super().setUp()

        # SHOP CREATION
        self.shop1 = Shop.objects.create(
            name="shop1", description="The first shop ever", color="#F4FA58")
        chiefs = Group.objects.create(name='chiefs-' + self.shop1.name)

        content_type = ContentType.objects.get(app_label='users', model='user')
        Permission.objects.create(
            name='Gérer le groupe des chiefs du magasin ' + self.shop1.name,
            codename='manage_group_chiefs-' + self.shop1.name,
            content_type=content_type
        )
        manage_associate_perm = Permission.objects.create(
            name='Gérer le groupe des associés du magasin ' + self.shop1.name,
            codename='manage_group_associates-' + self.shop1.name,
            content_type=content_type
        )

        # Add chiefs default permissions
        for codename in DEFAULT_PERMISSIONS_CHIEFS:
            perm = Permission.objects.get(codename=codename)
            chiefs.permissions.add(perm)

        chiefs.permissions.add(manage_associate_perm)
        chiefs.save()

        self.user3.groups.add(chiefs)

        self.product1 = Product.objects.create(
            name="skoll", shop=self.shop1)
        self.product2 = Product.objects.create(
            name="beer", unit='CL', shop=self.shop1, is_manual=True, manual_price=2)
        self.product3 = Product.objects.create(
            name="meat", unit='G', shop=self.shop1)


class BaseGeneralShopViewsTest(BaseShopsViewsTest):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ShopListViewTest(BaseGeneralShopViewsTest):
    url_view = 'url_shop_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopCreateViewTest(BaseGeneralShopViewsTest):
    url_view = 'url_shop_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class BaseFocusShopViewsTest(BaseShopsViewsTest):
    """
    Implement tests for views when focusing on a shop.
    """
    url_view = None

    def as_president_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_client1.status_code, 200)

    def as_chief_get(self):
        response_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_client3.status_code, 200)

    def not_existing_shop_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'presidents', 'pk': '5353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'specials', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(reverse(self.url_view, kwargs={
            'group_name': 'presidents', 'pk': str(self.shop1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ShopUpdateViewTest(BaseFocusShopViewsTest):
    url_view = 'url_shop_update'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopCheckupViewTest(BaseFocusShopViewsTest):
    url_view = 'url_shop_checkup'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class BaseGeneralProductViewsTest(BaseShopsViewsTest):
    url_view = None

    def president_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def chief_get(self):
        response_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductListViewTest(BaseGeneralProductViewsTest):
    url_view = 'url_product_list'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ProductCreateViewTest(BaseGeneralProductViewsTest):
    url_view = 'url_product_create'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class BaseFocusProductViewsTest(BaseShopsViewsTest):
    """
    Implement tests for views when focusing on a product.
    """
    url_view = None

    def as_president_get(self):
        response1_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': str(self.product1.pk)}))
        response2_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': str(self.product2.pk)}))
        response3_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': str(self.product3.pk)}))
        self.assertEqual(response1_client1.status_code, 200)
        self.assertEqual(response2_client1.status_code, 200)
        self.assertEqual(response3_client1.status_code, 200)

    def as_chief_get(self):
        response1_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.product1.pk)}))
        response2_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.product2.pk)}))
        response3_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.product3.pk)}))
        self.assertEqual(response1_client3.status_code, 200)
        self.assertEqual(response2_client3.status_code, 200)
        self.assertEqual(response3_client3.status_code, 200)

    def not_existing_product_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'presidents', 'pk': '5353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': str(self.product1.pk)}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.product1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'specials', 'pk': str(self.product1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(reverse(self.url_view, kwargs={
            'group_name': 'presidents', 'pk': str(self.product1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductRetrieveViewTest(BaseFocusProductViewsTest):
    url_view = 'url_product_retrieve'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_product_get(self):
        super().not_existing_product_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ProductUpdateViewTest(BaseFocusProductViewsTest):
    url_view = 'url_product_update'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_product_get(self):
        super().not_existing_product_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ProductUpdatePriceViewTest(BaseFocusProductViewsTest):
    url_view = 'url_product_update_price'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_product_get(self):
        super().not_existing_product_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ProductDeactivateViewTest(BaseFocusProductViewsTest):
    url_view = 'url_product_deactivate'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_product_get(self):
        super().not_existing_product_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ProductRemoveViewTest(BaseFocusProductViewsTest):
    url_view = 'url_product_remove'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()
        
    def test_not_existing_product_get(self):
        super().not_existing_product_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()