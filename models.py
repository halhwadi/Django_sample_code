import uuid
from datetime import date
# from django.contrib.postgres.fields import ArrayField
# from django.utils import timezone
from datetime import datetime

from account.models import Registration_Model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models import Q
from django.shortcuts import get_list_or_404
# from account.models import Registration_Model
# from django.urls import reverse
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField
# from django.contrib.gis.db import models
# from django import forms
from vehicle.models import Countries, Cities, truck_type
from api.models import ImageModel


class LoadModel(models.Model):
    types = [("FTL", "Full TruckLoad"), ("PTL", "Partial TruckLoad"), ("LTL", "Less Than TruckLoad")]
    status_options = [("1", "active"), ("2", "assigned"), ("3", "expired"),  ("4", "on_hold")]
    unit = [("1", "Pounds"), ("2", "Kilogram")]

    created_by = models.ForeignKey(Registration_Model, on_delete=models.CASCADE, related_name="load")
    assigned_to = models.ForeignKey(Registration_Model, on_delete=models.CASCADE, related_name="load_assigned_to", blank=True, null=True)
    uu_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False)
    slug = models.SlugField(null=False, unique=True, editable=False)
    load_type = models.CharField(max_length=3, choices=types, null=False, blank=False, default=None)
    truck_type = models.ForeignKey(truck_type, on_delete=models.CASCADE, related_name='load')
    number_of_trucks = models.IntegerField(default=1)
    weight_unit = models.CharField(max_length=15, choices=unit, default=1)
    weight = models.IntegerField()
    material = models.CharField(max_length=40, null=False, blank=False)
    material_image = models.ImageField(upload_to='load', null=True, blank=True, validators=[validate_image_file_extension])
    image_api = models.ForeignKey(ImageModel, on_delete=models.SET_NULL, related_name="load", null=True, blank=True)
    pickup_date = models.DateField(null=False, blank=False)
    pickup_time = models.TimeField(null=False, blank=False)
    dropoff_date = models.DateField(null=False, blank=False)
    dropoff_time = models.TimeField(null=False, blank=False)
    mobile_number = PhoneNumberField(blank=True,null=True)
    share_mobile = models.BooleanField(default=True)
    country_pickup = models.ManyToManyField(Countries, related_name="country_pickup")
    state_pickup = models.ManyToManyField(Cities, related_name="state_pickup")
    postalcode_pickup = models.CharField(max_length=20, null=True, blank=True,
                                  help_text="Only Zipcode or Postalcode(Optional)")
    coordinates_pickup = models.CharField(max_length=70, null=True, blank=True)
    location_pickup = models.CharField(max_length=3000, null=False, blank=True, default="No Details")
    country_dropoff = models.ManyToManyField(Countries, related_name="country_dropoff")
    state_dropoff = models.ManyToManyField(Cities, related_name="state_dropoff")
    postalcode_dropoff = models.CharField(max_length=20, null=True, blank=True,
                                         help_text="Only Zipcode or Postalcode(Optional)")
    coordinates_dropoff = models.CharField(max_length=70, null=True, blank=True)
    location_dropoff = models.CharField(max_length=3000, null=False, blank=True, default="No Details")
    distance = models.DecimalField(decimal_places=2, default=0.0, max_digits=8)
    status = models.CharField(max_length=15, choices=status_options, default="1")
    views = models.IntegerField(default=0)
    weight_qs = models.IntegerField(default=0)
    domain = models.CharField(max_length=1, default="1")  # 1 for demostic, 2 for international
    qout_number = models.IntegerField(default=0)
    qout_avg = models.DecimalField(decimal_places=2, default=0.0, max_digits=8)
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created_by.firstname}-{self.id}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.uu_id)

        if self.weight_unit == "2":
            self.weight = int(self.weight * 2.20462)
            self.weight_unit = "1"

        if self.truck_type.id != 3:
            if self.weight > 40000:
                self.weight_qs = 39000
            else:
                self.weight_qs = self.weight
        else:
            if self.weight > 52000:
                self.weight_qs = 51000
            else:
                self.weight_qs = self.weight

        if self.status != "3":
            if date.today() > self.dropoff_date:
                self.status = "3"
            elif date.today() == self.dropoff_date:
                now = datetime.now().time()
                if now >= self.dropoff_time:
                    self.status = "3"

        self.rate = self.created_by.rate

        return super().save(*args, **kwargs)

    def incrementViewCount(self, *args, **kwargs):
        self.views += 1 
        return super(LoadModel, self).save(*args, **kwargs)


class RemoveLoadModel(models.Model):
    user = models.ForeignKey(Registration_Model, on_delete=models.CASCADE, related_name='removed_loads')
    load_id = ArrayField(models.IntegerField(blank=False, null=False))


class LocationModel(models.Model):
    carrier = models.ForeignKey(Registration_Model, on_delete=models.CASCADE, related_name='location')
    load = models.ForeignKey(LoadModel, on_delete=models.CASCADE, related_name='carrier_location')
    coordinates = models.CharField(max_length=70, blank=True, null=True)
    allow_track = models.BooleanField(default=False)
    date = models.DateTimeField()

    def __str__(self):
        return f'{self.carrier}-{self.load}'

    def save(self, *args, **kwargs):

        try:
            locations = get_list_or_404(LocationModel, Q(carrier=self.carrier), ~Q(load=self.load))
        except:
            pass
        else:
            if len(locations) > 0:
                for loc in locations:
                    if loc.load.status != "3":
                        if date.today() > loc.load.dropoff_date:
                            loc.load.status = "3"
                            loc.load.save()
                            loc.delete()
                        elif date.today() == loc.load.dropoff_date:
                            now = datetime.now().time()
                            if now >= loc.load.dropoff_time:
                                loc.load.status = "3"
                                loc.load.save()
                                loc.delete()
                    elif loc.load.status == "3":
                        loc.delete()

                    elif not loc.allow_track:
                        loc.delete()

        return super().save(*args, **kwargs)


