from django.shortcuts import render
from order.models import LoadModel, RemoveLoadModel, LocationModel
from account.models import Registration_Model
from chat.models import Notifications, Connected
from order.forms import loadform, PickupForm, DropoffForm, Imageform
from vehicle.models import Countries,Cities,truck_type,truck_class
from geopy.geocoders import Nominatim
from functools import partial
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import JsonResponse
from django.contrib import messages
import numpy as np
from geopy import distance
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
import json
from datetime import datetime
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache


#from django.core.exceptions import ValueError



def address(request):
    country_id,country_name,state_id,state_name,address = 0, None, 0, None, None
    city_name, details, postalcode, error = None, None, None, "We don't operate in this location,Remove this selection" \
                                                              " and try again if you have mistakenly selected it"

    # city_list = ['city', 'region', 'county', 'state_district', 'village','suburb','city_district', 'road',
    #              'district', 'town', 'building', ]
    country_state_list = ['country', 'state', 'country_code', 'postcode']

    coordinates = request.GET.get('coordinates')
    geolocator = Nominatim(user_agent="Bikum")
    reverse = partial(geolocator.reverse, language="en-us")
    try:
        address = reverse(coordinates, timeout=5, addressdetails=True)
    except ValueError:
        error = "Must be a coordinate pair or Point,Ex:44.52,-64,29"
        country_id, state_id = -1, -1
        print(error)
        return JsonResponse(
            {'country_name': country_name, 'country_id': country_id, "state_name": state_name,
             "state_id": state_id, "city_name": city_name, 'postalcode': postalcode, "location": address,
             "error": error})
    else:
        print(address)  # pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
        address = address.raw['address'] if address is not None else(address)
        print(address) #ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
        if address is not None:
            country_code = address['country_code']
            print(country_code) #PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
            try:
                country_code_qs = Countries.objects.get(alpha_2code__icontains=country_code)
                print(country_code_qs) #ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            except:
                return JsonResponse(
                    {'country_name': country_name, 'country_id': country_id, "state_name": state_name,
                     "state_id": state_id, "city_name": city_name, 'postalcode': postalcode, "location": address,
                     "error": error})
            else:
                if country_code_qs:
                    country_id = country_code_qs.id
                    print(country_id)#ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                    country_name = country_code_qs.name
                    print(country_name) #pppppppppppppppppppppppppppppppppppppppppppppppppppppp

                    if any(["state" in k for k in address.keys()]):
                        index = np.where(["state" in k for k in address.keys()])[0].max()
                        state = list(address.values())[index]
                        print(state)#ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                        state_name_qs = Cities.objects.filter(Q(name__icontains=state), Q(country=country_code_qs))
                        if len(state_name_qs) > 1:
                            state_name_qs = Cities.objects.filter(Q(name=state), Q(country=country_code_qs))
                        print('state_name_qs',state_name_qs)# ppppppppppppppppppppppppppppppppppppppppppppppp
                        if len(state_name_qs) == 1:
                            state_name = get_object_or_404(state_name_qs).name
                            print(state_name)#pppppppppppppppppppppppppppppppppppppppppppppp
                            state_id =  get_object_or_404(state_name_qs).id
                            print(state_id) #ppppppppppppppppppppppppppppppppppppppppppppppp
                            city_name = [f'{address[k]}' for k in address.keys() if k not in country_state_list]
                            city_name = city_name if len(city_name) != 0 else (None)
                            print(city_name)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                            postalcode = address['postcode'] if 'postcode' in address.keys() else(None)
                            print('postalcode', postalcode)#pppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                            error = None
                        # This block need to be added when new field has been added rather than state to restrict results
                        elif any(["territory" in k for k in address.keys()]):
                            index = np.where(["territory" in k for k in address.keys()])[0].max()
                            state = list(address.values())[index]
                            print(state)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                            state_name_qs = Cities.objects.filter(Q(name__icontains=state), Q(country=country_code_qs))
                            if len(state_name_qs) > 1:
                                state_name_qs = Cities.objects.filter(Q(name=state), Q(country=country_code_qs))
                            print('state_name_qs', state_name_qs)  # ppppppppppppppppppppppppppppppppppppppppppppppp
                            if len(state_name_qs) == 1:
                                state_name = get_object_or_404(state_name_qs).name
                                print(state_name)  # pppppppppppppppppppppppppppppppppppppppppppppp
                                state_id = get_object_or_404(state_name_qs).id
                                print(state_id)  # ppppppppppppppppppppppppppppppppppppppppppppppp
                                city_name = [f'{address[k]}' for k in address.keys() if k not in country_state_list]
                                city_name = city_name if len(city_name) != 0 else (None)
                                print(city_name)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                                postalcode = address['postcode'] if 'postcode' in address.keys() else (None)
                                print('postalcode', postalcode)  # pppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                                error = None
                    # This block need to be added when new field has been added rather than state to restrict results
                    elif any(["territory" in k for k in address.keys()]):
                        index = np.where(["territory" in k for k in address.keys()])[0].max()
                        state = list(address.values())[index]
                        print(state)#ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                        state_name_qs = Cities.objects.filter(Q(name__icontains=state), Q(country=country_code_qs))
                        if len(state_name_qs) > 1:
                            state_name_qs = Cities.objects.filter(Q(name=state), Q(country=country_code_qs))
                        print('state_name_qs',state_name_qs)# ppppppppppppppppppppppppppppppppppppppppppppppp
                        if len(state_name_qs) == 1:
                            state_name = get_object_or_404(state_name_qs).name
                            print(state_name)#pppppppppppppppppppppppppppppppppppppppppppppp
                            state_id =  get_object_or_404(state_name_qs).id
                            print(state_id) #ppppppppppppppppppppppppppppppppppppppppppppppp
                            city_name = [f'{address[k]}' for k in address.keys() if k not in country_state_list]
                            city_name = city_name if len(city_name) != 0 else (None)
                            print(city_name)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                            postalcode = address['postcode'] if 'postcode' in address.keys() else(None)
                            print('postalcode', postalcode)#pppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                            error = None
        return JsonResponse(
            {'country_name': country_name, 'country_id': country_id, "state_name": state_name,
             "state_id": state_id, "city_name": city_name,'postalcode': postalcode, "location": address, "error": error})


def state_location(request):
    error = None

    country_id = request.GET.get("country")
    print(country_id)
    country = get_object_or_404(Countries, id=country_id)
    print(country)
    country_name = country.name
    state_id = request.GET.get("state")
    print(state_id)
    state_name = get_object_or_404(Cities, id=state_id).name
    print(state_name)
    geolocator = Nominatim(user_agent="Bikum")
    geocode = partial(geolocator.geocode, language="en")
    if state_name == 'Washington':
        location_state = geocode({'state': state_name}, country_codes=country.alpha_2code, timeout=5,
                       extratags=True, addressdetails=True)
    else:
        location_state = geocode(state_name, country_codes=country.alpha_2code, timeout=5,
                                 extratags=True, addressdetails=True)
    if location_state is None:
        error = "There is no available details for this state, please try using search box," \
                " Zip/Postal Code box or map to select the location"
        location_country = geocode(country_name, country_codes=country.alpha_2code, timeout=5,
                       extratags=True, addressdetails=True)
        box = location_country.raw['boundingbox']
        viewbox = [(box[0], box[2]), (box[1], box[3])]
        print(viewbox)
        print(location_country.raw)
        lat = location_country.latitude
        lon = location_country.longitude
        location = location_country.raw['address']
    else:
        box = location_state.raw['boundingbox']
        print(box)
        viewbox = [(box[0], box[2]), (box[1], box[3])]
        print(viewbox)
        print(location_state.raw)
        lat = location_state.latitude
        lon = location_state.longitude
        print(lat, lon)
        location = location_state.raw['address']
    print('error',error)
    return JsonResponse({"lat": lat, "lon": lon, "location": location , "viewbox": viewbox,
                         "error": error})


def city_location(request, viewbox):
    country_id = request.GET.get("country")
    print(country_id)
    country = get_object_or_404(Countries, id=country_id)
    print(country)
    state_id = request.GET.get("state")
    print(state_id)
    state_name = get_object_or_404(Cities, id=state_id).name
    print(state_name)
    city_name = request.GET.get("city")
    print(city_name)
    geolocator = Nominatim(user_agent="Bikum")
    geocode = partial(geolocator.geocode, language="en")

    location = geocode(city_name, country_codes=country.alpha_2code,timeout=5, exactly_one=True, addressdetails=True,
                       viewbox=viewbox, bounded=True, extratags=True)
    print(location)
    latlon = request.GET.get('coordinates').split(',')
    print(latlon)
    lat = location.latitude if location is not None else(latlon[0])
    lon = location.longitude if location is not None else(latlon[1])
    error = location == None
    print(lat, lon)
    if location is None:
        reverse = partial(geolocator.reverse, language="en-us")
        location = reverse((lat, lon), timeout=5, addressdetails=True)
        print(location)
    else:
        address = location.raw['address']
        print("reach")
        if any(["state" in k for k in address.keys()]):
            index = np.where(["state" in k for k in address.keys()])[0].max()
            state = list(address.values())[index]
            print(state)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            error = state != state_name
            lat = location.latitude if not error else (latlon[0])
            lon = location.longitude if not error else (latlon[1])
            print(lat,lon)
            if error:
                reverse = partial(geolocator.reverse, language="en-us")
                location = reverse((lat, lon), timeout=5, addressdetails=True)
                print(location)
                # This block need to be added when new field has been added rather than state to restrict results
                if any(["territory" in k for k in address.keys()]):
                    error = False
                    index = np.where(["territory" in k for k in address.keys()])[0].max()
                    state = list(address.values())[index]
                    print(state)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
                    error = state != state_name
                    lat = location.latitude if not error else (latlon[0])
                    lon = location.longitude if not error else (latlon[1])
                    print(lat, lon)
                    if error:
                        reverse = partial(geolocator.reverse, language="en-us")
                        location = reverse((lat, lon), timeout=5, addressdetails=True)
                        print(location)
        # This block need to be added when new field has been added rather than state to restrict results
        elif any(["territory" in k for k in address.keys()]):
            index = np.where(["territory" in k for k in address.keys()])[0].max()
            state = list(address.values())[index]
            print(state)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            error = state != state_name
            lat = location.latitude if not error else (latlon[0])
            lon = location.longitude if not error else (latlon[1])
            print(lat,lon)
            if error:
                reverse = partial(geolocator.reverse, language="en-us")
                location = reverse((lat, lon), timeout=5, addressdetails=True)
                print(location)
    return JsonResponse({"lat": lat, "lon": lon, "location": location.raw['address'], "state": state_name, "error": error}, status=200)

def postalcode(request, viewbox):
    country_id = request.GET.get("country")
    print(country_id)
    country = get_object_or_404(Countries, id=country_id)
    print(country)
    state_id = request.GET.get("state")
    print(state_id)
    state_name = get_object_or_404(Cities, id=state_id).name
    print(state_name)
    city_name = request.GET.get("city")
    print(city_name)
    postalcode = request.GET.get("postalcode")
    print(postalcode)
    geolocator = Nominatim(user_agent="Bikum")
    geocode = partial(geolocator.geocode, language="en")

    location = geocode({"postalcode": postalcode}, timeout=5, country_codes=country.alpha_2code, exactly_one=True,
                       addressdetails=True, viewbox=viewbox, bounded=True, extratags=True)
    print(location)
    latlon = request.GET.get('coordinates').split(',')
    print(latlon)
    lat = location.latitude if location is not None else(latlon[0])
    lon = location.longitude if location is not None else(latlon[1])
    error = location == None
    print(lat, lon)
    if location is None:
        reverse = partial(geolocator.reverse, language="en-us")
        location = reverse((lat, lon), timeout=5, addressdetails=True)
        print(location)
    else:
        address = location.raw['address']
        print("reach")
        if any(["state" in k for k in address.keys()]):
            index = np.where(["state" in k for k in address.keys()])[0].max()
            state = list(address.values())[index]
            print(state)  # ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            error = state != state_name
            lat = location.latitude if not error else (latlon[0])
            lon = location.longitude if not error else (latlon[1])
            print(lat,lon)
            if error:
                reverse = partial(geolocator.reverse, language="en-us")
                location = reverse((lat, lon), timeout=5, addressdetails=True)
                print(location)
    return JsonResponse({"lat": lat, "lon": lon, "location": location.raw['address'], "state": state_name, "error": error}, status=200)

# def details(request):
#     country_id = request.GET.get("country")
#     print(country_id)
#     country = get_object_or_404(Countries, id=country_id)
#     print(country)
#     state_id = request.GET.get("state")
#     print(state_id)
#     state_name = get_object_or_404(Cities, id=state_id).name
#     print(state_name)
#     city_name = request.GET.get("city")
#     print(city_name)
#     postalcode = request.GET.get("postalcode")
#     print(postalcode)
#     details = request.GET.get("details")
#     print(details)
#     geolocator = Nominatim(user_agent="Bikum")
#     geocode = partial(geolocator.geocode, language="en")
#     location_state = geocode(state_name, country_codes=country.alpha_2code, timeout=5,
#                              extratags=True)
#     box = location_state.raw['boundingbox']
#     print(box)
#     viewbox = [(box[0], box[2]), (box[1], box[3])]
#     print(viewbox)
#     location = geocode(details, timeout=5, country_codes=country.alpha_2code, exactly_one=True, addressdetails=True,
#                        viewbox=viewbox, bounded=True, extratags=True)
#     print(location)
#     latlon = request.GET.get('coordinates').split(',')
#     print(latlon)
#     lat = location.latitude if location is not None else(latlon[0])
#     lon = location.longitude if location is not None else(latlon[1])
#     error = location == None
#     print(lat, lon)
#     if location is None:
#         reverse = partial(geolocator.reverse, language="en-us")
#         location = reverse((lat, lon), timeout=5, addressdetails=True)
#         print(location)
#     return JsonResponse({"lat": lat, "lon": lon, "location": location.raw['address'], "error": error}, status=200)


def load_cities(request):
    Country_id = request.GET.get('Country_id')
    state = Cities.objects.filter(country_id=Country_id)
    return render(request, 'city_dropdown_list_options.html', {'cities': state})
    # return JsonResponse(list(cities.values('id', 'name')), safe=False)

def shipper_check_fun(user):
    return user.is_authenticated and not get_object_or_404(Registration_Model, email=user.email).IsDriver

@user_passes_test(shipper_check_fun)
def create_load(request):
    user= get_object_or_404(Registration_Model, email=request.user.email)
    mobile = user.mobile_number if user.mobile_number is not None else(None)
    form = loadform(initial={'mobile_number': mobile})
    if request.method == "POST":
        form = loadform(request.POST, request.FILES)
        if form.is_valid():
            request.session['load_type'] = form.cleaned_data['load_type']
            request.session['truck_type_id'] = form.cleaned_data['truck_type'].id
            request.session['weight_unit'] = form.cleaned_data['weight_unit']
            request.session['weight'] = form.cleaned_data['weight']
            request.session['material'] = form.cleaned_data['material']
            request.session['pickup_date'] = form.cleaned_data['pickup_date']
            request.session['pickup_time'] = form.cleaned_data['pickup_time']
            request.session['dropoff_date'] = form.cleaned_data['dropoff_date']
            request.session['dropoff_time'] = form.cleaned_data['dropoff_time']
            request.session['number_of_trucks'] = form.cleaned_data['number_of_trucks']

            #mobile_number argument to next view function
            mobile = str(form.cleaned_data['mobile_number'])

            # serializing
            request.session['pickup_date'] = json.dumps(request.session['pickup_date'], cls= DjangoJSONEncoder)
            request.session['pickup_time'] = json.dumps(request.session['pickup_time'], cls=DjangoJSONEncoder)
            request.session['dropoff_date'] = json.dumps(request.session['dropoff_date'], cls=DjangoJSONEncoder)
            request.session['dropoff_time'] = json.dumps(request.session['dropoff_time'], cls=DjangoJSONEncoder)
            request.session['forward'] = True

            return redirect('pickup', mobile)
        else:
            errors = form.errors
            messages.error(request, "Check the error/s below")
            return render(request, 'load_create_form.html', context={"form": form, "errors": errors})

    return render(request, 'load_create_form.html', context={"form": form})

@user_passes_test(shipper_check_fun)
def pickup(request,mobile):
    if not request.session['forward']:
        return redirect('load')

    form = PickupForm()
    if request.method == 'POST':
        form = PickupForm(request.POST, request.FILES)

        if form.is_valid():
            coordinates_pickup = form.cleaned_data['coordinates_pickup']
            geolocator = Nominatim(user_agent="Bikum")
            reverse = partial(geolocator.reverse, language="en-us")
            address_pickup = reverse(coordinates_pickup, timeout=5, addressdetails=True).raw['address']
            address = ""
            for key, value in address_pickup.items():
                address = address + "-" + value
                address = address.strip("-")
            request.session['country_pickup_id'] = get_object_or_404(form.cleaned_data['country_pickup']).id
            request.session['state_pickup_id'] = get_object_or_404(form.cleaned_data['state_pickup']).id
            request.session['postalcode_pickup'] = form.cleaned_data['postalcode_pickup']
            request.session['coordinate_pickup'] = form.cleaned_data['coordinates_pickup']
            request.session['location_pickup'] = address


            return redirect('dropoff', mobile)
        else:
            errors = form.errors['state_pickup']
            return render(request, 'pickup.html', context={'form': form, "errors": errors})
    else:
        return render(request,'pickup.html', context={'form': form})

@user_passes_test(shipper_check_fun)
def dropoff(request, mobile):
    if not request.session['forward']:
        return redirect('load')

    form = DropoffForm()
    if request.method == 'POST':
        truck_type_obj = get_object_or_404(truck_type, id=request.session['truck_type_id'])
        country_pickup_obj = Countries.objects.filter(id=request.session['country_pickup_id'])
        state_pickup_obj = Cities.objects.filter(id=request.session['state_pickup_id'])

        #deselaizing
        pickup_date_de = datetime.strptime(request.session['pickup_date'][1:-1], '%Y-%m-%d').date()
        pickup_time_de = datetime.strptime(request.session['pickup_time'][1:-1],'%H:%M:%S').time()
        dropoff_date_de = datetime.strptime(request.session['dropoff_date'][1:-1],'%Y-%m-%d').date()
        dropoff_time_de = datetime.strptime(request.session['dropoff_time'][1:-1],'%H:%M:%S').time()


        load_instance = LoadModel(load_type=request.session['load_type'], truck_type=truck_type_obj,
                             number_of_trucks=request.session['number_of_trucks'],
                             weight_unit=request.session['weight_unit'], weight=request.session['weight'],
                             material=request.session['material'],
                             pickup_date=pickup_date_de, pickup_time=pickup_time_de,
                             dropoff_date=dropoff_date_de, dropoff_time=dropoff_time_de,
                             postalcode_pickup=request.session['postalcode_pickup'],
                             coordinates_pickup=request.session['coordinate_pickup'],
                             location_pickup=request.session['location_pickup'], mobile_number=mobile)

        load_instance.created_by = get_object_or_404(Registration_Model, email=request.user.email)
        load_instance.save()
        load_instance.country_pickup.set(country_pickup_obj)
        load_instance.state_pickup.set(state_pickup_obj)

        form = DropoffForm(request.POST, request.FILES, instance=load_instance)

        if form.is_valid():
            coordinates_dropoff = form.cleaned_data['coordinates_dropoff']
            geolocator = Nominatim(user_agent="Bikum")
            reverse = partial(geolocator.reverse, language="en-us")
            address_dropoff = reverse(coordinates_dropoff, timeout=5, addressdetails=True).raw['address']
            address = ""
            for key, value in address_dropoff.items():
                address = address + "-" + value
                address = address.strip("-")
            load_instance.country_dropoff.set(form.cleaned_data['country_dropoff'])
            load_instance.state_dropoff.set(form.cleaned_data['state_dropoff'])
            load_instance.postalcode_dropoff = form.cleaned_data['postalcode_dropoff']
            load_instance.coordinates_dropoff = form.cleaned_data['coordinates_dropoff']
            load_instance.location_dropoff = address
            distance_mile_km = distance.distance(request.session['coordinate_pickup'], form.cleaned_data['coordinates_dropoff']).miles
            load_instance.distance = distance_mile_km

            load_instance.save()
            request.session['load_id'] = load_instance.id

            messages.success(request, f'Your load number {load_instance.id} has been created successfully,'
                                      f'Click OK if you want to upload image for material, Otherwise click Cancel')
            request.session['forward'] = False

            return redirect('uploadimage')
        else:
            errors = form.errors
            return render(request, 'dropoff.html', context={'form': form, "errors": errors})
    else:
        return render(request, 'dropoff.html', context={'form': form})

@user_passes_test(shipper_check_fun)
def Uploadimage(request):
    form = Imageform()
    if request.method == 'POST':
        form= Imageform(request.POST, request.FILES, instance=LoadModel.objects.get(id=request.session['load_id']))

        if form.is_valid():

            if len(request.FILES) == 0:
                messages.error(request,"No image has been attached, please click OK to choose image or click cancel")
                return render(request, "Imageload.html", context={"form": form, "image": False})
            else:
                form.save()
                messages.success(request, 'Image has been uploaded successfully')
                return redirect('login')
        else:
            errors = form.errors
            return render(request, "Imageload.html", context={"form": form, "errors": errors})
    else:
        return render(request, "Imageload.html", context={"form": form, "image": True})



# Carrier list and details views----------------------------------------------------------------------------------
class carrier_check(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):

        if self.request.user.is_authenticated:
            user = get_object_or_404(Registration_Model, email=self.request.user.email)
            return user.IsDriver and user.has_vehicle
        else:
            return False

class LoadListViewCarrier(carrier_check, ListView):
    model = LoadModel
    allow_empty = True
    template_name = "Load_List_Carrier.html"
    ordering = ['-Date', '-rate']

    def get_queryset(self):
        try:
            get_list_or_404(Connected, user=self.request.user)
        except:
            print('user is not connected')
            pass
        else:
            user_list = get_list_or_404(Connected, user=self.request.user)
            for user in user_list:
                user.delete()
                print("user has been removed from Connected model")

        driver = Registration_Model.objects.get(email=self.request.user.email)

        if driver.vehicle.domain == "2":
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
        else:
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                if driver.vehicle.domain == "2":
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                        Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
                else:
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                        Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                        Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        try:
            qs2 = get_object_or_404(RemoveLoadModel, user=driver)  #Removed loads
        except:
            pass
        else:
            qs = qs.exclude(id__in=qs2.load_id)
        qs_initial = qs

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)

        load_type_id = ""
        country_pickup_id = ""
        state_pickup_id = ""
        country_dropoff_id = ""
        state_dropoff_id = ""
        load_status_id = ""

        try:
            self.request.META['HTTP_REFERER'].split("&")[1:]
        except:
            pass
        else:
            x_url = self.request.META['HTTP_REFERER'].split("&")[1:]
            for key in x_url:
                if 'load_type' in key:
                    idx_load_type = key.find("=") + 1
                    load_type_id = key[idx_load_type:]
                if 'country_pickup' in key:
                    idx_country_pickup = key.find("=") + 1
                    country_pickup_id = int(key[idx_country_pickup:]) if key[idx_country_pickup:] != "" else key[
                                                                                                             idx_country_pickup:]
                if 'state_pickup' in key:
                    idx_state_pickup = key.find("=") + 1
                    state_pickup_id = int(key[idx_state_pickup:]) if key[idx_state_pickup:] != "" else key[
                                                                                                       idx_state_pickup:]
                if 'country_dropoff' in key:
                    idx_country_dropoff = key.find("=") + 1
                    country_dropoff_id = int(key[idx_country_dropoff:]) if key[idx_country_dropoff:] != "" else key[
                                                                                                                idx_country_dropoff:]
                if 'state_dropoff' in key:
                    idx_state_dropoff = key.find("=") + 1
                    state_dropoff_id = int(key[idx_state_dropoff:]) if key[idx_state_dropoff:] != "" else key[
                                                                                                          idx_state_dropoff:]
                if 'load_status' in key:
                    idx_load_status = key.find("=") + 1
                    load_status_id = key[idx_load_status:]

        load_type = self.request.GET.get('load_type')
        if (load_type is not None) and (load_type != ""):
            qs = qs.filter(load_type=load_type)
        elif load_type_id != "":
            qs = qs.filter(load_type=load_type_id)
        else:
            pass

        country_pickup = self.request.GET.get('country_pickup')
        if (country_pickup is not None) and (country_pickup != ""):
            qs = qs.filter(country_pickup=country_pickup)
        elif country_pickup_id != "":
            qs = qs.filter(country_pickup=country_pickup_id)
        else:
            pass

        state_pickup = self.request.GET.get('state_pickup')
        if (state_pickup is not None) and (state_pickup != ""):
            qs = qs.filter(state_pickup=state_pickup)
        elif state_pickup_id != "":
            qs = qs.filter(state_pickup=state_pickup_id)
        else:
            pass

        country_dropoff = self.request.GET.get('country_dropoff')
        if (country_dropoff is not None) and (country_dropoff != ""):
            qs = qs.filter(country_dropoff=country_dropoff)
        elif country_dropoff_id != "":
            qs = qs.filter(country_dropoff=country_dropoff_id)
        else:
            pass

        state_dropoff = self.request.GET.get('state_dropoff')
        if (state_dropoff is not None) and (state_dropoff != ""):
            qs = qs.filter(state_dropoff=state_dropoff)
        elif state_dropoff_id != "":
            qs = qs.filter(state_dropoff=state_dropoff_id)
        else:
            pass

        status = self.request.GET.get('load_status')
        if (status is not None) and (status != ""):
            qs = qs.filter(status=status)
        elif load_status_id != "":
            qs = qs.filter(status=load_status_id)
        else:
            pass

        load_id = self.request.GET.get('load_id') or ""
        if load_id.isdigit():
            qs1 = qs.filter(id=load_id)
            qs = qs1 if len(qs1) > 0 else qs
            if len(qs1) == 0:
                messages.error(self.request, "There is no load with this number,"
                                             "Please check assigned loads page if this load has been assigned to you")

        return qs, qs_initial


    def get_context_data(self, **kwargs):
        context = super(LoadListViewCarrier, self).get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        qs, qs_initial = self.get_queryset()
        context['qs'] = qs
        context['country_pickup'] = []
        context['state_pickup'] = []
        context['country_dropoff'] = []
        context['state_dropoff'] = []
        context['load_type'] = []
        context['load_id'] = ""
        context['number_of_loads'] = 0
        context['qs_initial'] = len(qs) == len(qs_initial)

        if len(qs) != 0:
            objects = get_list_or_404(qs)

            for obj in objects:
                context['country_pickup'] = context['country_pickup'] + [country for country in obj.country_pickup.all() if country not in context['country_pickup']]
                context['state_pickup'] = context['state_pickup'] + [state for state in obj.state_pickup.all() if state not in context['state_pickup']]
                context['country_dropoff'] = context['country_dropoff'] + [country for country in obj.country_dropoff.all() if country not in context['country_dropoff']]
                context['state_dropoff'] = context['state_dropoff'] + [state for state in obj.state_dropoff.all() if state not in context['state_dropoff']]
                context['load_type'] = context['load_type'] + [type for type in [obj.load_type] if type not in context['load_type']]
                context['number_of_loads'] += 1

        return context

    def get_ordering(self):
        extra_order = self.request.GET.get('order_by')
        self.ordering = extra_order if extra_order is not None or "" else(self.ordering)
        return self.ordering


class LoadListViewCarrierAssigned(carrier_check, ListView):
    model = LoadModel
    allow_empty = True
    template_name = "Load_List_Carrier_Assigned.html"
    ordering = ('-Date')

    def get_queryset(self):
        try:
            get_list_or_404(Connected, user=self.request.user)
        except:
            print('user is not connected')
            pass
        else:
            user_list = get_list_or_404(Connected, user=self.request.user)
            for user in user_list:
                user.delete()
                print("user has been removed from Connected model")

        driver = Registration_Model.objects.get(email=self.request.user.email)
        if driver.vehicle.domain == "2":
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
        else:
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                if driver.vehicle.domain == "2":
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                        Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
                else:
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                        Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                        Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        try:
            qs2 = get_object_or_404(RemoveLoadModel, user=driver)  #Removed loads
        except:
            pass
        else:
            qs = qs.exclude(id__in=qs2.load_id)
        qs_initial = qs

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)

        load_type_id = ""
        country_pickup_id = ""
        state_pickup_id = ""
        country_dropoff_id = ""
        state_dropoff_id = ""
        load_status_id = ""

        try:
            self.request.META['HTTP_REFERER'].split("&")[1:]
        except:
            pass
        else:
            x_url = self.request.META['HTTP_REFERER'].split("&")[1:]
            for key in x_url:
                if 'load_type' in key:
                    idx_load_type = key.find("=") + 1
                    load_type_id = key[idx_load_type:]
                if 'country_pickup' in key:
                    idx_country_pickup = key.find("=") + 1
                    country_pickup_id = int(key[idx_country_pickup:]) if key[idx_country_pickup:] != "" else key[
                                                                                                             idx_country_pickup:]
                if 'state_pickup' in key:
                    idx_state_pickup = key.find("=") + 1
                    state_pickup_id = int(key[idx_state_pickup:]) if key[idx_state_pickup:] != "" else key[
                                                                                                       idx_state_pickup:]
                if 'country_dropoff' in key:
                    idx_country_dropoff = key.find("=") + 1
                    country_dropoff_id = int(key[idx_country_dropoff:]) if key[idx_country_dropoff:] != "" else key[
                                                                                                                idx_country_dropoff:]
                if 'state_dropoff' in key:
                    idx_state_dropoff = key.find("=") + 1
                    state_dropoff_id = int(key[idx_state_dropoff:]) if key[idx_state_dropoff:] != "" else key[
                                                                                                          idx_state_dropoff:]
                if 'load_status' in key:
                    idx_load_status = key.find("=") + 1
                    load_status_id = key[idx_load_status:]

        load_type = self.request.GET.get('load_type')
        if (load_type is not None) and (load_type != ""):
            qs = qs.filter(load_type=load_type)
        elif load_type_id != "":
            qs = qs.filter(load_type=load_type_id)
        else:
            pass

        country_pickup = self.request.GET.get('country_pickup')
        if (country_pickup is not None) and (country_pickup != ""):
            qs = qs.filter(country_pickup=country_pickup)
        elif country_pickup_id != "":
            qs = qs.filter(country_pickup=country_pickup_id)
        else:
            pass

        state_pickup = self.request.GET.get('state_pickup')
        if (state_pickup is not None) and (state_pickup != ""):
            qs = qs.filter(state_pickup=state_pickup)
        elif state_pickup_id != "":
            qs = qs.filter(state_pickup=state_pickup_id)
        else:
            pass

        country_dropoff = self.request.GET.get('country_dropoff')
        if (country_dropoff is not None) and (country_dropoff != ""):
            qs = qs.filter(country_dropoff=country_dropoff)
        elif country_dropoff_id != "":
            qs = qs.filter(country_dropoff=country_dropoff_id)
        else:
            pass

        state_dropoff = self.request.GET.get('state_dropoff')
        if (state_dropoff is not None) and (state_dropoff != ""):
            qs = qs.filter(state_dropoff=state_dropoff)
        elif state_dropoff_id != "":
            qs = qs.filter(state_dropoff=state_dropoff_id)
        else:
            pass

        status = self.request.GET.get('load_status')
        if (status is not None) and (status != ""):
            qs = qs.filter(status=status)
        elif load_status_id != "":
            qs = qs.filter(status=load_status_id)
        else:
            pass

        load_id = self.request.GET.get('load_id') or ""
        if load_id.isdigit():
            qs1 = qs.filter(id=load_id)
            qs = qs1 if len(qs1) > 0 else qs
            if len(qs1) == 0:
                messages.error(self.request, "There is no load with this number in assigned loads,"
                                             "Please check in your home page where all non assigned loads available")


        return qs, qs_initial

    def get_context_data(self, **kwargs):
        context = super(LoadListViewCarrierAssigned, self).get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        qs, qs_initial = self.get_queryset()
        context['qs'] = qs
        context['qs_initial'] = len(qs) == len(qs_initial)
        context['country_pickup'] = []
        context['state_pickup'] = []
        context['country_dropoff'] = []
        context['state_dropoff'] = []
        context['load_type'] = []
        context['status'] = []
        context['load_id'] = ""
        context['number_of_loads'] = 0

        if len(qs) != 0:
            objects = get_list_or_404(qs)

            for obj in objects:
                context['country_pickup'] = context['country_pickup'] + [country for country in obj.country_pickup.all() if country not in context['country_pickup']]
                context['state_pickup'] = context['state_pickup'] + [state for state in obj.state_pickup.all() if state not in context['state_pickup']]
                context['country_dropoff'] = context['country_dropoff'] + [country for country in obj.country_dropoff.all() if country not in context['country_dropoff']]
                context['state_dropoff'] = context['state_dropoff'] + [state for state in obj.state_dropoff.all() if state not in context['state_dropoff']]
                context['load_type'] = context['load_type'] + [type for type in [obj.load_type] if type not in context['load_type']]
                context['status'] = context['status'] + [status for status in obj.status if
                                                         status not in context['status']]
                context['number_of_loads'] += 1

        return context

    def get_ordering(self):
        extra_order = self.request.GET.get('order_by')
        self.ordering = extra_order if extra_order is not None or "" else(self.ordering)
        return self.ordering


class LoadDetailViewCarrier(carrier_check, DetailView):
    model = LoadModel
    template_name = 'LoadDetailViewCarrier.html'

    def get_queryset(self):
        driver = Registration_Model.objects.get(email=self.request.user.email)
        if driver.vehicle.domain == "2":
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
        else:
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                if driver.vehicle.domain == "2":
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                        Q(truck_type=driver.vehicle.Truck_Type), Q(status="1"),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
                else:
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                        Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                        Q(truck_type=driver.vehicle.Truck_Type), Q(status="1"),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        return qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.incrementViewCount()
        try:
            user = get_object_or_404(Registration_Model, email=self.request.user.email)
            get_list_or_404(Notifications, Q(sender=1) & Q(slug=obj.slug) & Q(user=user))
        except:
            pass
        else:
            notifications = get_list_or_404(Notifications,Q(sender=1) & Q(slug=obj.slug) & Q(user=user))
            for nots in notifications:
                nots.delete()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        return context


class LoadDetailViewCarrierAssigned(carrier_check, DetailView):
    model = LoadModel
    template_name = 'LoadDetailViewCarrierAssigned.html'

    def get_queryset(self):
        driver = Registration_Model.objects.get(email=self.request.user.email)
        if driver.vehicle.domain == "2":
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
        else:
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                Q(assigned_to=driver), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                if driver.vehicle.domain == "2":
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                        Q(truck_type=driver.vehicle.Truck_Type), Q(assigned_to=driver),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
                else:
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                        Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                        Q(truck_type=driver.vehicle.Truck_Type), Q(assigned_to=driver),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        return qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.incrementViewCount()
        try:
            user = get_object_or_404(Registration_Model, email=self.request.user.email)
            get_list_or_404(Notifications, Q(sender=1) & Q(slug=obj.slug) & Q(user=user))
        except:
            pass
        else:
            notifications = get_list_or_404(Notifications, Q(sender=1) & Q(slug=obj.slug) & Q(user=user))
            for nots in notifications:
                nots.delete()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        return context


class LoadListViewCarrierMap(carrier_check, ListView):

    model = LoadModel
    allow_empty = True
    template_name = "Load_List_Carrier_Map.html"
    ordering = ('-Date')

    def get_queryset(self):
        driver = Registration_Model.objects.get(email=self.request.user.email)
        if driver.vehicle.domain == "2":
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
        else:
            qs = LoadModel.objects.filter(
                Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                if driver.vehicle.domain == "2":
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) | Q(country_dropoff=driver.vehicle.Country),
                        Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))
                else:
                    qs = LoadModel.objects.filter(
                        Q(country_pickup=driver.vehicle.Country) & Q(country_dropoff=driver.vehicle.Country),
                        Q(state_pickup=driver.vehicle.City) | Q(state_dropoff=driver.vehicle.City),
                        Q(status="1"), Q(truck_type=driver.vehicle.Truck_Type),
                        Q(weight_qs__lte=driver.vehicle.Truck_Class.value), Q(domain=driver.vehicle.domain))

        try:
            qs2 = get_object_or_404(RemoveLoadModel, user=driver)  #Removed loads
        except:
            pass
        else:
            qs = qs.exclude(id__in=qs2.load_id)
        qs_initial = qs

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)

        load_type_id = ""
        country_pickup_id = ""
        state_pickup_id = ""
        country_dropoff_id = ""
        state_dropoff_id = ""
        load_status_id = ""

        try:
            self.request.META['HTTP_REFERER'].split("&")[1:]
        except:
            pass
        else:
            x_url = self.request.META['HTTP_REFERER'].split("&")[1:]
            for key in x_url:
                if 'load_type' in key:
                    idx_load_type = key.find("=") + 1
                    load_type_id = key[idx_load_type:]
                if 'country_pickup' in key:
                    idx_country_pickup = key.find("=") + 1
                    country_pickup_id = int(key[idx_country_pickup:]) if key[idx_country_pickup:] != "" else key[
                                                                                                             idx_country_pickup:]
                if 'state_pickup' in key:
                    idx_state_pickup = key.find("=") + 1
                    state_pickup_id = int(key[idx_state_pickup:]) if key[idx_state_pickup:] != "" else key[
                                                                                                       idx_state_pickup:]
                if 'country_dropoff' in key:
                    idx_country_dropoff = key.find("=") + 1
                    country_dropoff_id = int(key[idx_country_dropoff:]) if key[idx_country_dropoff:] != "" else key[
                                                                                                                idx_country_dropoff:]
                if 'state_dropoff' in key:
                    idx_state_dropoff = key.find("=") + 1
                    state_dropoff_id = int(key[idx_state_dropoff:]) if key[idx_state_dropoff:] != "" else key[
                                                                                                          idx_state_dropoff:]
                if 'load_status' in key:
                    idx_load_status = key.find("=") + 1
                    load_status_id = key[idx_load_status:]

        load_type = self.request.GET.get('load_type')
        if (load_type is not None) and (load_type != ""):
            qs = qs.filter(load_type=load_type)
        elif load_type_id != "":
            qs = qs.filter(load_type=load_type_id)
        else:
            pass

        country_pickup = self.request.GET.get('country_pickup')
        if (country_pickup is not None) and (country_pickup != ""):
            qs = qs.filter(country_pickup=country_pickup)
        elif country_pickup_id != "":
            qs = qs.filter(country_pickup=country_pickup_id)
        else:
            pass

        state_pickup = self.request.GET.get('state_pickup')
        if (state_pickup is not None) and (state_pickup != ""):
            qs = qs.filter(state_pickup=state_pickup)
        elif state_pickup_id != "":
            qs = qs.filter(state_pickup=state_pickup_id)
        else:
            pass

        country_dropoff = self.request.GET.get('country_dropoff')
        if (country_dropoff is not None) and (country_dropoff != ""):
            qs = qs.filter(country_dropoff=country_dropoff)
        elif country_dropoff_id != "":
            qs = qs.filter(country_dropoff=country_dropoff_id)
        else:
            pass

        state_dropoff = self.request.GET.get('state_dropoff')
        if (state_dropoff is not None) and (state_dropoff != ""):
            qs = qs.filter(state_dropoff=state_dropoff)
        elif state_dropoff_id != "":
            qs = qs.filter(state_dropoff=state_dropoff_id)
        else:
            pass

        status = self.request.GET.get('load_status')
        if (status is not None) and (status != ""):
            qs = qs.filter(status=status)
        elif load_status_id != "":
            qs = qs.filter(status=load_status_id)
        else:
            pass

        load_id = self.request.GET.get('load_id') or ""
        if load_id.isdigit():
            qs1 = qs.filter(id=load_id)
            qs = qs1 if len(qs1) > 0 else qs
            if len(qs1) == 0:
                messages.error(self.request, "There is no load with this number, Please check assigned loads page if this load has been assigned to you")

        return qs, qs_initial

    def get_context_data(self, **kwargs):
        context = super(LoadListViewCarrierMap, self).get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        qs, qs_initial = self.get_queryset()
        context['qs'] = qs
        context['qs_initial'] = len(qs) == len(qs_initial)
        context['country_pickup'] = []
        context['state_pickup'] = []
        context['country_dropoff'] = []
        context['state_dropoff'] = []
        context['load_type'] = []
        context['load_id'] = ""
        context['coordinates_pickup'] = []
        context['coordinates_dropoff'] = []
        context['number_of_loads'] = 0

        if len(qs) != 0:
            objects = get_list_or_404(qs)

            for obj in objects:
                context['country_pickup'] = context['country_pickup'] + [country for country in obj.country_pickup.all() if country not in context['country_pickup']]
                context['state_pickup'] = context['state_pickup'] + [state for state in obj.state_pickup.all() if state not in context['state_pickup']]
                context['country_dropoff'] = context['country_dropoff'] + [country for country in obj.country_dropoff.all() if country not in context['country_dropoff']]
                context['state_dropoff'] = context['state_dropoff'] + [state for state in obj.state_dropoff.all() if state not in context['state_dropoff']]
                context['load_type'] = context['load_type'] + [type for type in [obj.load_type] if type not in context['load_type']]
                context['number_of_loads'] += 1

            for load in qs:
                if load.coordinates_pickup is not None:
                    context['coordinates_pickup'] += [load.coordinates_pickup + "," + load.slug + "N"]
                else:
                    pass
                if load.coordinates_dropoff is not None:
                    context['coordinates_dropoff'] += [load.coordinates_dropoff + "," + load.slug + "N"]
                else:
                    pass
        return context

    def get_ordering(self):
        extra_order = self.request.GET.get('order_by')
        self.ordering = extra_order if extra_order is not None or "" else(self.ordering)
        return self.ordering



# Shipper Load list and details views--------------------------------------------------------------------------------
class shipper_check(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        if self.request.user.is_authenticated:
            user = get_object_or_404(Registration_Model, email=self.request.user.email)
            return not user.IsDriver
        else:
            return False


class LoadListShipperView(shipper_check, ListView):

    model = LoadModel
    allow_empty = True
    template_name = "Load_List_Shipper.html"
    ordering = ('-Date')

    def get_queryset(self):
        try:
            get_list_or_404(Connected, user=self.request.user)
        except:
            print('user is not connected')
            pass
        else:
            user_list = get_list_or_404(Connected, user=self.request.user)
            for user in user_list:
                user.delete()
                print("user has been removed from Connected model")

        shipper = Registration_Model.objects.get(email=self.request.user.email)
        qs = LoadModel.objects.filter(created_by=shipper)

        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True

            if status_change:
                qs = LoadModel.objects.filter(created_by=shipper)

        try:
            qs2 = get_object_or_404(RemoveLoadModel, user=shipper)  # Removed loads
        except:
            pass
        else:
            qs = qs.exclude(id__in=qs2.load_id)
        qs_initial = qs

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)

        load_type_id = ""
        country_pickup_id = ""
        state_pickup_id = ""
        country_dropoff_id = ""
        state_dropoff_id = ""
        load_status_id = ""
        assigned_loads_id = ""
        truck_type_id = ""

        try:
            self.request.META['HTTP_REFERER'].split("&")[1:]
        except:
            pass
        else:
            x_url = self.request.META['HTTP_REFERER'].split("&")[1:]
            for key in x_url:
                if 'load_type' in key:
                    idx_load_type = key.find("=") + 1
                    load_type_id = key[idx_load_type:]
                if 'country_pickup' in key:
                    idx_country_pickup = key.find("=") + 1
                    country_pickup_id = int(key[idx_country_pickup:]) if key[idx_country_pickup:] != "" else key[idx_country_pickup:]
                if 'state_pickup' in key:
                    idx_state_pickup = key.find("=") + 1
                    state_pickup_id = int(key[idx_state_pickup:]) if key[idx_state_pickup:] != "" else key[idx_state_pickup:]
                if 'country_dropoff' in key:
                    idx_country_dropoff = key.find("=") + 1
                    country_dropoff_id = int(key[idx_country_dropoff:]) if key[idx_country_dropoff:] != "" else key[idx_country_dropoff:]
                if 'state_dropoff' in key:
                    idx_state_dropoff = key.find("=") + 1
                    state_dropoff_id = int(key[idx_state_dropoff:]) if key[idx_state_dropoff:] != "" else key[idx_state_dropoff:]
                if 'load_status' in key:
                    idx_load_status = key.find("=") + 1
                    load_status_id = key[idx_load_status:]
                if 'assigned_loads' in key:
                    idx_assigned_loads = key.find("=") + 1
                    assigned_loads_id = key[idx_assigned_loads:]
                if 'truck_type' in key:
                    idx_truck_type = key.find("=") + 1
                    truck_type_id = key[idx_truck_type:]

        truck_type = self.request.GET.get('truck_type')
        if truck_type is not None and truck_type != "":
            qs = qs.filter(truck_type=truck_type)
        elif truck_type_id != "":
            qs = qs.filter(truck_type=truck_type_id)

        load_type = self.request.GET.get('load_type')
        if (load_type is not None) and (load_type != ""):
            qs = qs.filter(load_type=load_type)
        elif load_type_id != "":
            qs = qs.filter(load_type=load_type_id)
        else:
            pass

        country_pickup = self.request.GET.get('country_pickup')
        if (country_pickup is not None) and (country_pickup != ""):
            qs = qs.filter(country_pickup=country_pickup)
        elif country_pickup_id != "":
            qs = qs.filter(country_pickup=country_pickup_id)
        else:
            pass

        state_pickup = self.request.GET.get('state_pickup')
        if (state_pickup is not None) and (state_pickup != ""):
            qs = qs.filter(state_pickup=state_pickup)
        elif state_pickup_id != "":
            qs = qs.filter(state_pickup=state_pickup_id)
        else:
            pass

        country_dropoff = self.request.GET.get('country_dropoff')
        if (country_dropoff is not None) and (country_dropoff != ""):
            qs = qs.filter(country_dropoff=country_dropoff)
        elif country_dropoff_id != "":
            qs = qs.filter(country_dropoff=country_dropoff_id)
        else:
            pass

        state_dropoff = self.request.GET.get('state_dropoff')
        if (state_dropoff is not None) and (state_dropoff != ""):
            qs = qs.filter(state_dropoff=state_dropoff)
        elif state_dropoff_id != "":
            qs = qs.filter(state_dropoff=state_dropoff_id)
        else:
            pass

        status = self.request.GET.get('load_status')
        if (status is not None) and (status != ""):
            qs = qs.filter(status=status)
        elif load_status_id != "":
            qs = qs.filter(status=load_status_id)
        else:
            pass

        assigned_loads = self.request.GET.get('assigned_loads')
        if assigned_loads == 'assigned':
            qs = qs.filter(~Q(assigned_to=None))
        elif assigned_loads_id != "":
            qs = qs.filter(~Q(assigned_to=None))

        load_id = self.request.GET.get('load_id') or ""
        if load_id.isdigit():
            qs1 = qs.filter(id=load_id)
            qs = qs1 if len(qs1) > 0 else qs
            if len(qs1) == 0:
                messages.error(self.request, "There is no load with this number")

        return qs, qs_initial

    def get_context_data(self, **kwargs):
        context = super(LoadListShipperView, self).get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        qs, qs_initial = self.get_queryset()
        context['qs'] = qs
        context['qs_initial'] = len(qs) == len(qs_initial)
        context['country_pickup'] = []
        context['state_pickup'] = []
        context['country_dropoff'] = []
        context['state_dropoff'] = []
        context['load_type'] = []
        context['truck_type'] = []
        context['status'] = []
        context['loads'] = []
        context['load_id'] = ""
        context['number_of_loads'] = 0

        # to get qs_initial to shown All loads button
        # shipper = Registration_Model.objects.get(email=self.request.user.email)
        # qs_initial = LoadModel.objects.filter(created_by=shipper)
        # try:
        #     qs2 = get_object_or_404(RemoveLoadModel, user=shipper)  # Removed loads
        # except:
        #     context['qs_initial'] = len(qs) == len(qs_initial)
        # else:
        #     qs_initial = qs_initial.exclude(id__in=qs2.load_id)
        #     context['qs_initial'] = len(qs) == len(qs_initial)



        if len(qs) != 0:
            objects = get_list_or_404(qs)

            for obj in objects:
                context['country_pickup'] = context['country_pickup'] + [country for country in obj.country_pickup.all() if country not in context['country_pickup']]
                context['state_pickup'] = context['state_pickup'] + [state for state in obj.state_pickup.all() if state not in context['state_pickup']]
                context['country_dropoff'] = context['country_dropoff'] + [country for country in obj.country_dropoff.all() if country not in context['country_dropoff']]
                context['state_dropoff'] = context['state_dropoff'] + [state for state in obj.state_dropoff.all() if state not in context['state_dropoff']]
                context['load_type'] = context['load_type'] + [type for type in [obj.load_type] if type not in context['load_type']]
                context['status'] = context['status'] + [status for status in obj.status if status not in context['status']]
                context['truck_type'] = context['truck_type'] + [type for type in [obj.truck_type.id] if type not in context['truck_type']]
                if obj.assigned_to != None and "assigned_only" not in context['loads']:
                    context['loads'] = ['assigned_only']
                context['number_of_loads'] += 1
        return context

    def get_ordering(self):
        extra_order = self.request.GET.get('order_by')
        self.ordering = extra_order if extra_order is not None or "" else(self.ordering)
        return self.ordering


class LoadDetailShipperView(shipper_check, DetailView):
    model = LoadModel
    template_name = 'LoadDetailShipperView.html'

    def get_queryset(self):
        shipper = Registration_Model.objects.get(email=self.request.user.email)
        qs = LoadModel.objects.filter(created_by=shipper)


        status_change = False
        if len(qs) != 0:
            for load in qs:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        status_change = True
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            status_change = True
            if status_change:
                qs = LoadModel.objects.filter(created_by=shipper)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user1'] = get_object_or_404(Registration_Model, email=self.request.user.email)
        return context

@login_required
def remove_load(request,load_id):
    link = request.META['HTTP_REFERER']

    try:
        user = get_object_or_404(Registration_Model,email=request.user.email)
    except:
        messages.error(request,"Profile issue, Please liaise with our support team")
        return redirect('login')
    else:
        try:
            load = get_object_or_404(LoadModel, id=load_id)
        except:
            messages.error(request, "This load is no more available")
            return redirect(link)
        else:
            if user.IsDriver:
                if load.status == "1":
                    link = 'Load_List_Carrier'
                else:
                    link = 'Load_List_Carrier_Assigned'
            else:
                link = 'Load_List_Shipper'

            try:
                user_loads = get_object_or_404(RemoveLoadModel, user=user)
            except:
                if user.IsDriver:
                    if load.status != "2":
                        RemoveLoadModel.objects.create(user=user, load_id=[load_id])
                        messages.success(request, f'Load {load.id} has been removed')
                        return redirect(link)
                    else:
                        messages.error(request, "You can not remove this load because its assigned to you")
                        return redirect(link)
                else:
                    if load.status in ["3", "4"]:
                        RemoveLoadModel.objects.create(user=user, load_id=[load_id])
                        messages.success(request, f'Load {load.id} has been removed')
                        return redirect(link)
                    else:
                        messages.error(request, "Only load which status is expired or on hold can be removed")
                        return redirect(link)
            else:
                if user.IsDriver:
                    if load.status != "2":
                        if load_id not in user_loads.load_id:
                            user_loads.load_id += [load_id]
                            user_loads.save()
                            messages.success(request, f'Load {load.id} has been removed')
                            return redirect(link)
                        else:
                            messages.success(request, f'Load {load.id} has been removed')
                            return redirect(link)
                    else:
                        messages.error(request, "You can not remove this load because its assigned to you")
                        return redirect(link)
                else:
                    if load.status in ["3", "4"]:
                        if load_id not in user_loads.load_id:
                            user_loads.load_id += [load_id]
                            user_loads.save()
                            messages.success(request, f'Load {load.id} has been removed')
                            return redirect(link)
                        else:
                            messages.success(request, f'Load {load.id} has been removed')
                            return redirect(link)
                    else:
                        messages.error(request, "Only load which status is expired or on hold can be removed")
                        return redirect(link)

@user_passes_test(shipper_check_fun)
def delete_load(request, load_id):
    try:
        load = get_object_or_404(LoadModel, id=load_id)
    except:
        messages.error(request, "This is load is no more available ")
        return redirect('login')
    else:
        try:
            shipper = get_object_or_404(Registration_Model,email=request.user.email)
        except:
            messages.error(request, "Profile issue, Please liaise with our support team")
            return redirect('login')
        else:
            if load.assigned_to:
                messages.warning(request, f'You cant delete this load because its already assigned to {load.assigned_to.firstname}')
                return redirect('login')
            else:
                messages.success(request, f'Load {load.id} has been deleted successfully')
                load.delete()
                return redirect('login')


@user_passes_test(shipper_check_fun)
def hold_load(request, load_id):
    try:
        load = get_object_or_404(LoadModel, id=load_id)
    except:
        messages.error(request, "This is load is no more available ")
        return redirect('login')
    else:
        try:
            shipper = get_object_or_404(Registration_Model,email=request.user.email)
        except:
            messages.error(request, "Profile issue, Please liaise with our support team")
            return redirect('login')
        else:
            if not load.assigned_to:
                if load.status == "1":
                    load.status = "4"
                    load.save()
                    messages.success(request, "You will not receive more quotations!")
                    return redirect('LoadDetailShipperView', load.slug)
                else:
                    if load.status == "2":
                        status = "Assigned"
                    elif load.status == "3":
                        status = "Expired"
                    elif load.status == "4":
                        status = "On Hold"
                    messages.info(request, f'You can not change load status because load status is {status}')
                    return redirect('LoadDetailShipperView', load.slug)
            else:
                messages.info(request,f'You will not receive more quotations because load is already assigned to {load.assigned_to.firstname})')
                return redirect('LoadDetailShipperView', load.slug)


@user_passes_test(shipper_check_fun)
def release_load(request, load_id):
    try:
        load = get_object_or_404(LoadModel, id=load_id)
    except:
        messages.error(request, "This is load is no more available ")
        return redirect('login')
    else:
        try:
            shipper = get_object_or_404(Registration_Model,email=request.user.email)
        except:
            messages.error(request, "Profile issue, Please liaise with our support team")
            return redirect('login')
        else:
            if load.assigned_to:
                messages.info(request, f'You cant resume receiving quotations because load is assigned to {load.assigned_to.firstname}')
                return redirect('LoadDetailShipperView', load.slug)
            else:
                if load.status == "4":
                    if load.pickup_date < date.today():
                        messages.error(request, f'Can not release this load because its pickup date is due, please create new load with new dates')
                        return redirect('LoadDetailShipperView', load.slug)
                    else:
                        load.status = "1"
                        load.save()
                        messages.success(request, "Load has been released!")
                        return redirect('LoadDetailShipperView', load.slug)
                elif load.status == "3":
                    messages.info(request, f'This load is already expired')
                    return redirect('LoadDetailShipperView', load.slug)
                elif load.status == "1":
                    messages.info(request, f'This load is already released')
                    return redirect('LoadDetailShipperView', load.slug)

@login_required
def allow_track_location(request, load_id):
    try:
        carrier = get_object_or_404(Registration_Model, email=request.user.email)
    except:
        messages.error(request, "Profile issue, Please liaise with support team")
        return redirect('login')
    else:
        try:
            load = get_object_or_404(LoadModel, id=load_id)
        except:
            messages.info("Load is no more available")
            return redirect('login')
        else:
            if load.status != "3":
                if date.today() > load.dropoff_date:
                    load.status = "3"
                    load.save()
                elif date.today() == load.dropoff_date:
                    now = datetime.now().time()
                    if now >= load.dropoff_time:
                        load.status = "3"
                        load.save()

            if carrier != load.assigned_to:
                messages.warning(request, "Authorization Restriction!!")
                return redirect('login')
            if not load.assigned_to:
                messages.info(request, "Location tracking is not applicable for non assigned loads")
                return redirect('login')

            if load.status != "2":
                messages.info(request, "Tracking location service is not applicable for this load because its"
                                       " Dropoff date and time is already due")
                return redirect('LoadDetailViewCarrierAssigned', load.slug)

            if load.pickup_date < date.today():
                try:
                    location = get_object_or_404(LocationModel, Q(carrier=carrier), Q(load=load))
                except:
                    location = LocationModel(carrier=carrier, load=load, allow_track=True)
                    location.date = datetime.now()
                    location.save()
                    messages.success(request, "Tracking location service has been enabled for this load")
                    return redirect('fetch_location', load.id)
                else:
                    if not location.allow_track:
                        location.allow_track = True
                        location.date = datetime.now()
                        location.save()
                        messages.success(request, "Sharing location service has started for this load")
                        return redirect('fetch_location', load.id)
                    else:
                        messages.success(request, "Sharing location service has started for this load")
                        return redirect('fetch_location', load.id)
            elif load.pickup_date == date.today():
                if load.pickup_time <= datetime.now().time():
                    try:
                        location = get_object_or_404(LocationModel, Q(carrier=carrier), Q(load=load))
                    except:
                        location = LocationModel(carrier=carrier, load=load, allow_track=True)
                        location.date = datetime.now()
                        location.save()
                        messages.success(request, "Tracking location service has been enabled for this load")
                        return redirect('fetch_location', load.id)
                    else:
                        if not location.allow_track:
                            location.allow_track = True
                            location.date = datetime.now()
                            location.save()
                            messages.success(request, "Sharing location service has started for this load")
                            return redirect('fetch_location', load.id)
                        else:
                            messages.success(request, "Sharing location service has started for this load")
                            return redirect('fetch_location', load.id)
                else:
                    messages.info(request, "Tracking service for this load will be enabled once pickup_time is due")
                    return redirect('LoadDetailViewCarrierAssigned', load.slug)
            else:
                messages.info(request, "Tracking service for this load will be enabled once pickup_date is due")
                return redirect('LoadDetailViewCarrierAssigned', load.slug)


@login_required
def fetch_location(request, load_id):
    try:
        carrier = get_object_or_404(Registration_Model, email=request.user.email)
    except:
        messages.error(request, "Profile issue, Please liaise with support team")
        return redirect('login')
    else:
        try:
            load = get_object_or_404(LoadModel, id=load_id)
        except:
            messages.info("Load is no more available")
            return redirect('login')
        else:
            try:
                location = get_object_or_404(LocationModel, carrier=carrier, load=load)
            except:
                messages.error(request, "If this load is not expired then make sure you have enabled "
                                        "location tracking service for it")
                return redirect('LoadDetailViewCarrierAssigned', load.slug)
            else:
                if load.status != "3":
                    if date.today() > load.dropoff_date:
                        load.status = "3"
                        load.save()
                        location.delete()
                        messages.info(request, "Tracking location service has been stopped for this load because its"
                                               " Dropoff date has been due")
                        return redirect('LoadDetailViewCarrierAssigned', load.slug)
                    elif date.today() == load.dropoff_date:
                        now = datetime.now().time()
                        if now >= load.dropoff_time:
                            load.status = "3"
                            load.save()
                            location.delete()
                            messages.info(request,
                                          "Tracking location service has been stopped for this load because its"
                                          " Dropoff date and time has been due")
                            return redirect('LoadDetailViewCarrierAssigned', load.slug)
                if location.allow_track:
                    return render(request, 'track_location_carrier.html',
                                  context={'location': location, 'load': load, 'carrier': carrier})

@login_required
def ajax_fetch_coordinates(request, location_id):
    coordinates = request.GET.get('coordinates')
    print('coordinates', coordinates)
    try:
        location = get_object_or_404(LocationModel, id=location_id)
    except:
        return JsonResponse({'status': "Failed"})
    else:
        location.coordinates = coordinates
        location.date = datetime.now()
        location.save()
        print('fetch location', location.coordinates)
        return JsonResponse({'status': "success"})


@login_required
def carrier_location(request, load_id):
    try:
        load = get_object_or_404(LoadModel, id=load_id)
    except:
        messages.error(request, "This Load is no more available")
        return redirect('login')
    else:
        if load.assigned_to and load.status != "3":
            locations = load.carrier_location.all()

            if len(locations) > 0:
                for location in locations:
                    print('location.coordinates', location.coordinates)
                    try:
                        user = get_object_or_404(Registration_Model, email=request.user.email)
                    except:
                        messages.error(request, "Profile issue liaise with support team")
                        return redirect('login')
                    else:
                        if user == load.created_by:
                          return render(request, 'carrier_location.html', context={'location': location,
                                                                                   'load': load, 'shipper': user})
                        else:
                            messages.warning(request, "Authorization restriction")
                            return redirect('LoadDetailShipperView', load.slug)
            else:
                messages.info(request, f'{load.assigned_to.firstname} did not share his/her location, liaise with him/her to share his/her location')
                return redirect('LoadDetailShipperView', load.slug)
        elif load.assigned_to and load.status == "3":
            messages.info(request, "Tracking location for expired load is not allowed")
            return redirect('LoadDetailShipperView', load.slug)
        else:
            messages.info(request, "Tracking location for non assigned load is not possibe")
            return redirect('LoadDetailShipperView', load.slug)

@login_required
def ajax_extract_coordinates(request, location_id):
    try:
        location = get_object_or_404(LocationModel, id=location_id)
    except:
        return JsonResponse({'status': "Failed"})
    else:
        coordinates = location.coordinates
        print('extract location',coordinates )
        date = location.date
        return JsonResponse({'coordinates': coordinates, 'date': date, 'status': 'Success'})