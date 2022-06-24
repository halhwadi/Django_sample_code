import sys
# import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'Bikum.settings'
#sys.path.append('C:\\Users\\Husam.Alhwadi\\django_projects\\Bikum\\')
from django.urls import path, re_path
from order import views
from django.conf.urls.static import static
from Bikum import settings
from account.views import service_worker


urlpatterns = [
path('service-worker.js', service_worker),  # To pin App on home screen
path('load', views.create_load, name='load'),
path('pickup/<str:mobile>', views.pickup, name='pickup'),
path('dropoff/<str:mobile>', views.dropoff, name='dropoff'),
path('uploadimage', views.Uploadimage, name='uploadimage'),
path('address', views.address, name='address'),
path('state_location', views.state_location, name='state_location'),
re_path(r'^city_location/(?P<viewbox>)/$', views.city_location, name='city_location'),
re_path(r'^postalcode/(?P<viewbox>)/$', views.postalcode, name='postalcode'),
path('loadlistcarrier', views.LoadListViewCarrier.as_view(), name='Load_List_Carrier'),
path('loadlistcarriermap', views.LoadListViewCarrierMap.as_view(), name='Load_List_Carrier_Map'),
path('loadlistcarrierassigned', views.LoadListViewCarrierAssigned.as_view(), name='Load_List_Carrier_Assigned'),
path('loadlistshipper', views.LoadListShipperView.as_view(), name='Load_List_Shipper'),
path('loadcarrier/<slug:slug>', views.LoadDetailViewCarrier.as_view(), name='LoadDetailViewCarrier'),
path('loadlistcarrierassigned/<slug:slug>', views.LoadDetailViewCarrierAssigned.as_view(), name='LoadDetailViewCarrierAssigned'),
path('loadshipper/<slug:slug>', views.LoadDetailShipperView.as_view(), name='LoadDetailShipperView'),
path('remove_load/<int:load_id>',views.remove_load, name='remove_load'),
path('delete_load/<int:load_id>', views.delete_load, name='delete_load'),
path('hold_load/<int:load_id>', views.hold_load, name='hold_load'),
path('release_load/<int:load_id>', views.release_load, name='release_load'),
path('allow_track_location/<int:load_id>', views.allow_track_location, name="allow_track_location"),
path('fetch_location/<int:load_id>', views.fetch_location, name='fetch_location'),
path('ajax_fetch_coordinates/<int:location_id>', views.ajax_fetch_coordinates, name='ajax_fetch_coordinates'),
path('carrier_location/<int:load_id>', views.carrier_location, name='carrier_location'),
path('ajax_extract_coordinates/<int:location_id>', views.ajax_extract_coordinates, name='ajax_extract_coordinates'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

