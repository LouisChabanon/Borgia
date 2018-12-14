import datetime
import functools
import json
import re
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import FormView

from borgia.utils import (INTERNALS_GROUP_NAME, GroupLateralMenuMixin,
                          LateralMenuMixin,
                          get_managers_group_from_user, is_association_manager)
from events.models import Event
from finances.models import ExceptionnalMovement, Recharging, Sale, Transfert
from modules.models import OperatorSaleModule, SelfSaleModule
from shops.models import Shop
from users.forms import UserQuickSearchForm
from users.models import User


class ModulesLoginView(LoginView):
    """ Override of auth login view, to include direct login to sales modules """
    redirect_authenticated_user = True

    def add_next_to_login(self, path_next, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
        """
        Add the given 'path_next' path to the 'login_url' path.
        """
        resolved_url = resolve_url(login_url or settings.LOGIN_URL)

        login_url_parts = list(urlparse(resolved_url))
        if redirect_field_name:
            querystring = QueryDict(login_url_parts[4], mutable=True)
            querystring[redirect_field_name] = path_next
            login_url_parts[4] = querystring.urlencode(safe='/')

        return urlunparse(login_url_parts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_theme'] = settings.DEFAULT_TEMPLATE

        context['shop_list'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            operator_module = shop.modules_operatorsalemodule_shop.first()
            operator_module_link = self.add_next_to_login(
                reverse('url_shop_module_sale', kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'}))
            self_module = shop.modules_selfsalemodule_shop.first()
            self_module_link = self.add_next_to_login(
                reverse('url_shop_module_sale', kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}))
            context['shop_list'].append({
                'shop': shop,
                'operator_module': operator_module,
                'operator_module_link' : operator_module_link,
                'self_module': self_module,
                'self_module_link' : self_module_link
            })
        return context


class MembersWorkboard(LateralMenuMixin, View):
    template_name = 'workboards/members_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        context['transaction_list'] = self.get_transactions()
        return render(request, self.template_name, context=context)

    def get_transactions(self):
        transactions = {'months': self.monthlist(
            datetime.datetime.now() - datetime.timedelta(days=365),
            datetime.datetime.now()), 'all': self.request.user.list_transaction()[:5]}

        # Shops sales
        sale_list = Sale.objects.filter(
            sender=self.request.user).order_by('-datetime')
        transactions['shops'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            list_filtered = sale_list.filter(shop=shop)
            total = 0
            for sale in list_filtered:
                total += sale.amount()
            transactions['shops'].append({
                'shop': shop,
                'total': total,
                'sale_list_short': list_filtered[:5],
                'data_months': self.data_months(list_filtered, transactions['months'])
            })

        # Transferts
        transfert_list = Transfert.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by('-datetime')
        transactions['transferts'] = {
            'transfert_list_short': transfert_list[:5]
        }

        # Rechargings
        rechargings_list = Recharging.objects.filter(
            sender=self.request.user).order_by('-datetime')
        transactions['rechargings'] = {
            'recharging_list_short': rechargings_list[:5]
        }

        # ExceptionnalMovements
        exceptionnalmovements_list = ExceptionnalMovement.objects.filter(
            recipient=self.request.user).order_by('-datetime')
        transactions['exceptionnalmovements'] = {
            'exceptionnalmovement_list_short': exceptionnalmovements_list[:5]
        }

        # Shared event
        events_list = Event.objects.filter(
            done=True, users=self.request.user).order_by('-datetime')
        for obj in events_list:
            obj.amount = obj.get_price_of_user(self.request.user)

        transactions['events'] = {
            'event_list_short': events_list[:5]
        }

        return transactions

    @staticmethod
    def data_months(mlist, months):
        amounts = [0 for _ in range(0, len(months))]
        for obj in mlist:
            if obj.datetime.strftime("%b-%y") in months:
                amounts[
                    months.index(obj.datetime.strftime("%b-%y"))] +=\
                    abs(obj.amount())
        return amounts

    @staticmethod
    def monthlist(start, end):
        def total_months(dt): return dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime.datetime(y, m+1, 1).strftime("%b-%y"))
        return mlist


class ManagersWorkboard(PermissionRequiredMixin, LateralMenuMixin, View):
    template_name = 'workboards/managers_workboard.html'
    lm_active = 'lm_workboard'

    def has_permission(self):
        return is_association_manager(self.request.user)

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        context['group'] = get_managers_group_from_user(request.user)
        context['sale_list'] = Sale.objects.all().order_by('-datetime')[:5]
        context['events'] = []
        for event in Event.objects.all():
            context['events'].append({
                'title': event.description,
                'start': event.date
            })

        # Form Quick user search
        context['quick_user_search_form'] = UserQuickSearchForm()
        return render(request, self.template_name, context=context)


def handler403(request, *args, **kwargs):
    context = {}

    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
    except IndexError:
        context['group_name'] = INTERNALS_GROUP_NAME
        context['group'] = Group.objects.get(name=INTERNALS_GROUP_NAME)
    except ObjectDoesNotExist:
        context['group_name'] = INTERNALS_GROUP_NAME
        context['group'] = Group.objects.get(name=INTERNALS_GROUP_NAME)

    try:
        if (request.user.groups.all().exclude(
                pk__in=[1, 5, 6]).count() > 0):
            context['first_job'] = request.user.groups.all().exclude(
                pk__in=[1, 5, 6])[0]
        context['list_selfsalemodule'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            try:
                module_sale = SelfSaleModule.objects.get(shop=shop)
                if module_sale.state is True:
                    context['list_selfsalemodule'].append(shop)
            except ObjectDoesNotExist:
                pass
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass

    response = render(
        request,
        '403.html',
        context=context)
    response.status_code = 403
    return response


def handler404(request, *args, **kwargs):
    context = {}
    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
        if (request.user.groups.all().exclude(
                pk__in=[1, 5, 6]).count() > 0):
            context['first_job'] = request.user.groups.all().exclude(
                pk__in=[1, 5, 6])[0]
        context['list_selfsalemodule'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            try:
                module_sale = SelfSaleModule.objects.get(shop=shop)
                if module_sale.state is True:
                    context['list_selfsalemodule'].append(shop)
            except ObjectDoesNotExist:
                pass
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass
    response = render(
        request,
        '404.html',
        context=context)
    response.status_code = 404
    return response


def handler500(request, *args, **kwargs):
    context = {}
    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass
    response = render(
        request,
        '500.html',
        context=context)
    response.status_code = 500
    return response


def get_list_model(request, model, search_in, props=None):
    """
    Permet de sérialiser en JSON les instances de modèle. Il est possible de
    donner des paramtères GET à cette fonction pour moduler
    la liste obtenue, plutôt que de faire un traitement en JS.
    Ne renvoie par les informations sensibles comme is_superuser ou password.

    :param request: GET: chaîne de caractère qui doit représenter une
                         recherche filter dans un des champs de model
    :type request: GET: doit être dans les champs de model
    Les paramètres spéciaux sont order_by pour trier et search pour chercher
    dans search_in
    :param model: Model dont on veut lister les instances
    :type model: héritée de models.Model
    :param search_in: paramètres dans lesquels le paramètre GET search sera
    recherché
    :type search_in: liste de chaînes de caractères
    :param props: méthodes du model à envoyer dans la sérialisation en
    supplément
    :type props: liste de chaînes de caractères de nom de méthodes de model
    :return HttpResponse(data): liste des instances de model sérialisé
    en JSON, modulée par les parametres

    Exemple :
    model = User
    search_in = ['username', 'last_name', 'first_name']
    request.GET = { 'family': '101-99', 'order_by': 'year' }
    renverra la liste des users dont la famille est 101-99
    en les triant par année
    """

    # Liste des filtres
    kwargs_filter = {}
    for param in request.GET:
        if param not in ['order_by', 'reverse', 'search']:
            if param in [f.name for f in model._meta.get_fields()]:
                # Traitement spécifique pour les booléens envoyés en GET
                if request.GET[param] in ['True', 'true', 'False', 'false']:
                    if request.GET[param] in ['True', 'true']:
                        kwargs_filter[param] = True
                    else:
                        kwargs_filter[param] = False
                else:
                    kwargs_filter[param] = request.GET[param]
    query = model.objects.filter(**kwargs_filter)

    # Recherche si précisée
    try:
        args_search = functools.reduce(
            lambda q, where: q | Q(
                **{where + '__startswith': request.GET['search']}), search_in,
            Q())
        query = query.filter(args_search).distinct()
    except KeyError:
        pass

    # Sérialisation
    if model is not User:

        data_serialise = serialize('json', query)

    else:  # Cas User traité à part car contient des fields sensibles

        # Suppression des users spéciaux
        query = query.exclude(
            Q(groups=Group.objects.get(pk=1)) | Q(username='admin'))

        # Sérialisation
        allowed_fields = [f.name for f in User._meta.get_fields()]
        for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
            allowed_fields.remove(e)

        data_serialise = serialize('json', query, fields=allowed_fields)

    data_load = json.loads(data_serialise)

    # Méthodes supplémentaires
    if props:
        for i, e in enumerate(data_load):
            props_dict = {}
            for p in props:
                try:
                    props_dict[p] = getattr(model.objects.get(pk=e['pk']), p)()
                except:
                    pass
            data_load[i]['props'] = props_dict

    # Trie si précisé
    try:
        if request.GET['reverse'] in ['True', 'true']:
            reverse_url = True
        else:
            reverse_url = False
        # Trie par la valeur d'un field
        if (request.GET['order_by']
                in [f.name for f in model._meta.get_fields()]):
            data_load = sorted(
                data_load,
                key=lambda obj: obj['fields'][request.GET['order_by']],
                reverse=reverse_url)
        # Trie par la valeur d'une méthode
        else:
            data_load = sorted(
                data_load,
                key=lambda obj: getattr(
                    model.objects.get(pk=obj['pk']),
                    request.GET['order_by'])(),
                reverse=reverse_url)
    except KeyError:
        pass

    # Information du nombre total d'élément
    count = len(data_load)

    # End et begin
    try:
        data_load = data_load[int(request.GET[
            'begin']):int(request.GET['end'])]
    except (KeyError, AttributeError):
        pass

    # Ajout de l'information du nombre total d'élément
    try:
        data_load[0]['count'] = count
    except IndexError:
        pass

    data = json.dumps(data_load)
    return HttpResponse(data)


def get_unique_model(request, pk, model, props=None):
    """
    Permet de sérialiser en JSON une instance spécifique pk=pk de model.
    Ne renvoie par les informations sensibles comme is_superuser ou password
    dans le cas d'un User.

    :param props:
    :param request:
    :param model: Model dont on veut lister les instances
    :type model: héritée de models.Model
    :param pk: pk de l'instance à retourner
    :type pk: integer > 0

    :return HttpResponse(data): l'instance de model sérialisé en JSON

    Exemple :
    model = User
    pk = 3
    renverra le json de l'user pk=3

    Remarque :
    serialise envoie une liste sérialisé, pour récupérer en js il ne faut
    pas faire data car c'est une liste, mais bien
    data[0]. Il n'y aura toujours que 1 élément dans cette liste car
    générée par un objects.get()
    """

    try:
        # On traite le cas particulier de User à part car des informations
        # sont sensibles
        if model is not User:

            # Sérialisation
            data = serialize('json', [model.objects.get(pk=pk), ])

        else:

            # Sérialisation
            allowed_fields = [f.name for f in User._meta.get_fields()]
            for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
                allowed_fields.remove(e)

            data_serialise = serialize('json', [User.objects.get(pk=pk), ],
                                       fields=allowed_fields)
            data_load = json.loads(data_serialise)

            if props:
                for i, e in enumerate(data_load):
                    props_dict = {}
                    for p in props:
                        try:
                            props_dict[p] = getattr(
                                model.objects.get(pk=e['pk']), p)()
                        except:
                            pass
                    data_load[i]['props'] = props_dict

            data = json.dumps(data_load)

    except ObjectDoesNotExist:
        data = [[]]

    return HttpResponse(data)
