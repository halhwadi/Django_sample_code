from django import template
from django.template.defaultfilters import stringfilter
# import json
import ast
from django.db.models import Avg
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from qoutation.models import QoutationModel
# from account.models import Registration_Model
from order.models import LoadModel
# from chat.models import Notifications
# from django.contrib import messages
from datetime import date
from django.db.models import Q
from reviews.models import ReviewsModel

register = template.Library()

@register.filter(name="abbreviation")
@stringfilter
def abbreviation(value):
    return len(value)

@register.filter(name="address")
@stringfilter
def address(value):
    if value[0] == "{":
        location_dict = ast.literal_eval(value)
        print(location_dict)
        address = ""
        for key, value in location_dict['address'].items():
            address = address + "-" + value
            address = address.strip("-")
    else:
        address=value
    return address.strip("-")

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):

    d = context['request'].GET.copy()

    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.simple_tag(name='check')
def check(load, user1):
    if user1:
        for qoutation in load.qoutation.all():
            if user1 == qoutation.createdby:
                return True
    return False

@register.simple_tag(name='qout_avg')
def qout_avg(load):
    if load.qoutation.all():
        qout_average = load.qoutation.all().aggregate(Avg('value'))['value__avg']
        qout_average = round(qout_average, 2) if qout_average is not None else 0
        qout = load.qoutation.all()[0]
        if qout.currency == '1':
            currency_apv = '$'
        elif qout.currency == '2':
            currency_apv = 'CA$'
        elif qout.currency == '3':
            currency_apv = '£'
        elif qout.currency == '4':
            currency_apv = 'ZAR'
        elif qout.currency == '5':
            currency_apv = 'NZ$'
        elif qout.currency == '6':
            currency_apv = 'AU$'
        elif qout.currency == '7':
            currency_apv = '€'
        elif qout.currency == '8':
            currency_apv = 'AED'
        return f'{qout_average} {currency_apv}'
    else:
        return 0

@register.simple_tag(name='qout_count')
def qout_count(load):
    qout_count = load.qoutation.count() or 0
    return qout_count

@register.simple_tag(name='qout_count_carrier')
def qout_count_carrier(load, user1):
    qout_count = load.qoutation.count() or 0
    if 0 < qout_count < 10:
        qout_count = 'less than 10'
    return qout_count

@register.simple_tag(name='qout_slug')
def qout_slug(load, user1):
    if user1:
        if load.qoutation.all():
            for qoutation in load.qoutation.all():
                if user1 == qoutation.createdby:
                    return qoutation.slug
            return None
        else:
            return None

@register.simple_tag(name='qout_val')
def qout_val(load):
    if load.qoutation.all():
        for qout in load.qoutation.all():
            if qout.currency == '1':
                currency_apv = '$'
            elif qout.currency == '2':
                currency_apv = 'CA$'
            elif qout.currency == '3':
                currency_apv = '£'
            elif qout.currency == '4':
                currency_apv = 'ZAR'
            elif qout.currency == '5':
                currency_apv = 'NZ$'
            elif qout.currency == '6':
                currency_apv = 'AU$'
            elif qout.currency == '7':
                currency_apv = '€'
            return f'{qout.value} {currency_apv}'
    else:
        return 0

@register.simple_tag(name='qout_nots')
def qout_nots(nots):
    if nots:
        try:
            qout = get_object_or_404(QoutationModel, slug=nots.slug)
        except:
            nots.delete()
            link = 'login'
            return link
        else:
            if nots.user.IsDriver:
                if qout.status != 2:
                    link = 'update_qoutation_carrier'
                else:
                    link = 'login'
            else:
                link = 'update_qoutation_shipper'

            return link
    else:
        link = 'login'
        return link

@register.simple_tag(name='load_link')
def load_link(nots):
    if nots:
        if nots.sender == '1':
            try:
                load = get_object_or_404(LoadModel, slug=nots.slug)
            except:
                print(nots.msg)
                nots.delete()
                link = 'login'
                return link
            else:
                if load.status == "2":
                    link = 'LoadDetailViewCarrierAssigned'
                elif load.status == "1":
                    link = 'LoadDetailViewCarrier'
                else:
                    nots.delete()
                    link = 'login'
                return link
        else:
            link = 'login'
            return link
    else:
        link = 'login'
        return link

@register.simple_tag(name='calendar')
def calendar(user):
    load_counts = None
    if user:
        if user.IsDriver:
            if len(user.load_assigned_to.all()) > 0:
                loads = user.load_assigned_to.all().filter(Q(status="2"), Q(pickup_date=date.today()) | Q(dropoff_date=date.today()))
                print('loads',loads)
                load_counts = len(loads) if len(loads) != 0 else None

        else:
            if len(user.load.all()) > 0:
                loads = user.load.all().filter(Q(status="2"), Q(pickup_date=date.today()) | Q(dropoff_date=date.today()))
                print('loads', loads)
                load_counts = len(loads) if len(loads) != 0 else None

    return load_counts

@register.simple_tag(name='rated_shipper')
def rated_shipper(load, shipper):
    carrier = load.assigned_to
    try:
        has_rated = get_object_or_404(ReviewsModel, Q(reviewer=shipper), Q(user=carrier))
    except:
        return False
    else:
        return True

@register.simple_tag(name='rated_carrier')
def rated_carrier(load, carrier):
    shipper = load.created_by
    try:
        has_rated = get_object_or_404(ReviewsModel, Q(reviewer=carrier), Q(user=shipper))
    except:
        return False
    else:
        return True

@register.simple_tag(name='new_review')
def new_review(nots):
    if nots:
        if '-' in nots.slug:
            return False
        else:
            return True

@register.simple_tag(name='user_id')
def user_id(nots):
    user_id = None
    if nots:
        if '-' in nots.slug:
            user_id = nots.slug.split("-")[0]
    return user_id

@register.simple_tag(name='room_name')
def room_name(load_id):
    try:
        load = get_object_or_404(LoadModel, id=load_id)
    except:
        return None
    else:
        try:
            if load.assigned_to:
                driver_id = get_object_or_404(User, email=load.assigned_to.email).id
            else:
                return None
        except:
            return None
        else:
            return f'{load_id}_{driver_id}'
