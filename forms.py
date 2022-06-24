import sys
sys.path.append("C:/Users/Husam.Alhwadi/django_projects/Bikum")

from account.models import Registration_Model
from order.models import LoadModel
from django import forms
from vehicle.models import Countries, Cities,truck_type,truck_class
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.shortcuts import render, redirect, get_object_or_404
from Bikum.settings import BASE_DIR
import os

#PickupForm
class M2MSelect(forms.SelectMultiple):
    allow_multiple_selected = False

class PickupForm(forms.ModelForm):

    class Meta:
        model = LoadModel
        fields = ['country_pickup', 'state_pickup', 'postalcode_pickup', 'coordinates_pickup']
        labels = {
            "postalcode_pickup": "Zip/Postal code",
            }
        widgets = {
            'country_pickup': M2MSelect(),
            'state_pickup': M2MSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country_pickup'].empty_label = ""
        self.fields['country_pickup'].queryset = Countries.objects.all().order_by('name')
        self.fields['state_pickup'].queryset = Cities.objects.none()

        if 'country_pickup' in self.data:
            try:
                Country_id = int(self.data.get('country_pickup'))
                self.fields['state_pickup'].queryset = Cities.objects.filter(country_id=Country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['state_pickup'].queryset = self.instance.Country.cities_set.order_by('name')


#Dropoff Form
class DropoffForm(forms.ModelForm):

    class Meta:
        model = LoadModel
        fields = ['country_dropoff', 'state_dropoff', 'postalcode_dropoff', 'coordinates_dropoff']
        labels = {
            "postalcode_dropoff": "Zip/Postal code",
        }
        widgets = {
            'country_dropoff': M2MSelect(),
            'state_dropoff': M2MSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country_dropoff'].empty_label = ""
        self.fields['country_dropoff'].queryset = Countries.objects.all().order_by('name')
        self.fields['state_dropoff'].queryset = Cities.objects.none()


        if 'country_dropoff' in self.data:
            try:
                Country_id = int(self.data.get('country_dropoff'))
                self.fields['state_dropoff'].queryset = Cities.objects.filter(country_id=Country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['state_dropoff'].queryset = self.instance.Country.cities_set.order_by('name')


#Load Form
class DateInput(forms.DateTimeInput):
    input_type = 'date'

class TimeInput(forms.DateTimeInput):
    input_type = 'time'

class CheckBox(forms.RadioSelect):
    input_type = "radio"


class loadform(forms.ModelForm):
    mobile_number = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='UAE'), required=True)

    class Meta:
        model = LoadModel
        exclude = ['uu_id', 'slug', 'views', 'distance', 'status', 'created_by', 'country_pickup', 'state_pickup',
                   'coordinates', 'location', 'postalcode', 'country_dropoff', 'state_dropoff', 'location_pickup',
                   'location_dropoff', 'postalcode_pickup', 'postalcode_dropoff', 'material_image', 'weight_qs',
                   'domain', 'assigned_to', 'rate', 'qout_avg', 'qout_number']
        labels = {
            "number_of_trucks": "Trucks Count",
        }
        widgets = {
            'pickup_date': DateInput(),
            'dropoff_date': DateInput(),
            "pickup_time": TimeInput(),
            "dropoff_time": TimeInput(),
            "truck_type": CheckBox(),
            "load_type": CheckBox()
        }

    def __init__(self, *args, **kwargs):
        #self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['truck_type'].queryset = truck_type.objects.all().order_by('order')


class Imageform(forms.ModelForm):

    class Meta:
        model = LoadModel
        fields = ['material_image']



