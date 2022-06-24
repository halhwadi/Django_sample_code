from django.contrib import admin
from order.models import LoadModel, RemoveLoadModel, LocationModel

# Register your models here.
admin.site.register(LoadModel)
admin.site.register(RemoveLoadModel)
admin.site.register(LocationModel)
