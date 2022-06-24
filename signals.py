from account.models import Registration_Model
from order.models import LoadModel
from django.db.models.signals import post_save, m2m_changed, pre_save
from chat.models import Notifications
from django.db.models import Q
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, get_list_or_404



# Update Shipper mobile number upon filling mobile number in create load form
@receiver(post_save, sender=LoadModel, dispatch_uid="LoadModel_to_Registration_Model_Mobile")
def update_Shipper_Mobile(sender, instance, created,update_fields, **kwargs):
    user = get_object_or_404(Registration_Model, id=instance.created_by.id)
    if instance.mobile_number is not None:
        if user.mobile_number != instance.mobile_number:
            user.mobile_number = instance.mobile_number
            user.save()

# Assign the value for load domian
@receiver(m2m_changed, sender=LoadModel.country_dropoff.through, dispatch_uid="LoadModel_domain")
def set_domain(sender, **kwargs):
    action = kwargs.pop('action', None)
    instance = kwargs.pop('instance', None)

    if action == "post_add":
        for country_pickup in instance.country_pickup.all():
            for country_dropoff in instance.country_dropoff.all():
                if country_pickup == country_dropoff:
                    pass
                else:
                    instance.domain = "2"
                    instance.save()


@receiver(m2m_changed, sender=LoadModel.state_dropoff.through, dispatch_uid="New_Load_Notification" )
def load_notification(sender, instance, action, **kwargs):
    print("m2m fired")
    if action == "post_add":
        drivers = Registration_Model.objects.filter(Q(IsDriver=True) & Q(has_vehicle=True))
        if instance.domain == "2":
            for driver in drivers:
                if driver.vehicle.domain == instance.domain:
                    if instance.status == "1":
                        if driver.vehicle.Truck_Type == instance.truck_type:
                            if driver.vehicle.Truck_Class.value >= instance.weight_qs:
                                country_found = False
                                for country_pickup in instance.country_pickup.all():
                                    if driver.vehicle.Country == country_pickup:
                                        msg = f'New load No.{instance.id}'
                                        Notifications.objects.create(user=driver, msg=msg, sender=1,
                                                                     slug=instance.slug)
                                        country_found = True
                                        break
                                for country_dropoff in instance.country_dropoff.all():
                                    if not country_found:
                                        if driver.vehicle.Country == country_dropoff:
                                            msg = f'New load No.{instance.id}'
                                            Notifications.objects.create(user=driver, msg=msg, sender=1,
                                                                         slug=instance.slug)
        else:
            for driver in drivers:
                print(driver)
                if driver.vehicle.domain == instance.domain:
                    print(instance.status, type(instance.status))
                    if instance.status == '1':
                        print("status passed")
                        for country_pickup in instance.country_pickup.all():
                            print("country_pickup", country_pickup, driver.vehicle.Country)
                            if driver.vehicle.Country == country_pickup:
                                for country_dropoff in instance.country_dropoff.all():
                                    print("country_dropoff", country_dropoff, driver.vehicle.Country)
                                    if driver.vehicle.Country == country_dropoff:
                                        if driver.vehicle.Truck_Type == instance.truck_type:
                                            print("Truck_Type")
                                            if driver.vehicle.Truck_Class.value >= instance.weight_qs:
                                                print("Truck class")
                                                state_found = False
                                                for state_pickup in instance.state_pickup.all():
                                                    print("state_pickup", state_pickup,driver.vehicle.City )
                                                    if driver.vehicle.City == state_pickup:
                                                        msg = f'New load No.{instance.id}'
                                                        Notifications.objects.create(user=driver, msg=msg, sender=1,
                                                                                     slug=instance.slug)
                                                        state_found = True
                                                        break
                                                for state_dropoff in instance.state_dropoff.all():
                                                    print("state_dropoff", instance.country_dropoff, driver.vehicle.City )
                                                    if not state_found:
                                                        if driver.vehicle.City == state_dropoff:
                                                            msg = f'New load No.{instance.id}'
                                                            Notifications.objects.create(user=driver, msg=msg, sender=1,
                                                                                         slug=instance.slug)


# Romeve LocationModel object once assigned loads is expired
@receiver(post_save, sender=LoadModel, dispatch_uid="LoadModel_to_LocationModel")
def remove_location_objects(sender, instance, created,update_fields, **kwargs):
    print("remove_location_object is triggered")
    if not created:
        if instance.status == "3" and instance.assigned_to:
            locations = instance.carrier_location.all()

            if len(locations) > 0:
                for loc in locations:
                    print(f'location {loc.id} has been deleted')
                    loc.delete()

@receiver(pre_save, sender=LoadModel, dispatch_uid="LoadModel_to_Notification")
def release_load_notification(sender, instance, raw, update_fields, **kwargs):
    if instance.id:
        load = LoadModel.objects.get(id=instance.id)
        if instance.status == "1" and load.status == "4":
            print("release load fired")
            drivers = Registration_Model.objects.filter(Q(IsDriver=True) & Q(has_vehicle=True))
            if instance.domain == "2":
                for driver in drivers:
                    if driver.vehicle.domain == instance.domain:
                        if instance.status == "1":
                            if driver.vehicle.Truck_Type == instance.truck_type:
                                if driver.vehicle.Truck_Class.value >= instance.weight_qs:
                                    country_found = False
                                    for country_pickup in instance.country_pickup.all():
                                        if driver.vehicle.Country == country_pickup:
                                            msg = f'load No.{instance.id} is receiving quotations now'
                                            Notifications.objects.get_or_create(user=driver, msg=msg, sender=1,
                                                                         slug=instance.slug)
                                            country_found = True
                                            break
                                    for country_dropoff in instance.country_dropoff.all():
                                        if not country_found:
                                            if driver.vehicle.Country == country_dropoff:
                                                msg = f'load No.{instance.id} is receiving quotations now'
                                                Notifications.objects.get_or_create(user=driver, msg=msg, sender=1,
                                                                             slug=instance.slug)
            else:
                for driver in drivers:
                    print(driver)
                    print("domain", driver.vehicle.domain, instance.domain)
                    if driver.vehicle.domain == instance.domain:
                        print(instance.status, type(instance.status))
                        if instance.status == '1':
                            print("status passed")
                            for country_pickup in instance.country_pickup.all():
                                print("country_pickup", country_pickup, driver.vehicle.Country)
                                if driver.vehicle.Country == country_pickup:
                                    for country_dropoff in instance.country_dropoff.all():
                                        print("country_dropoff", country_dropoff, driver.vehicle.Country)
                                        if driver.vehicle.Country == country_dropoff:
                                            if driver.vehicle.Truck_Type == instance.truck_type:
                                                print("Truck_Type")
                                                if driver.vehicle.Truck_Class.value >= instance.weight_qs:
                                                    print("Truck class")
                                                    state_found = False
                                                    for state_pickup in instance.state_pickup.all():
                                                        print("state_pickup", state_pickup, driver.vehicle.City)
                                                        if driver.vehicle.City == state_pickup:
                                                            msg = f'load No.{instance.id} is receiving quotations now'
                                                            Notifications.objects.get_or_create(user=driver, msg=msg,
                                                                                         sender=1,
                                                                                         slug=instance.slug)
                                                            state_found = True
                                                            break
                                                    for state_dropoff in instance.state_dropoff.all():
                                                        if not state_found:
                                                            if driver.vehicle.City == state_dropoff:
                                                                msg = f'load No.{instance.id} is receiving quotations now'
                                                                Notifications.objects.get_or_create(user=driver, msg=msg,
                                                                                             sender=1,
                                                                                             slug=instance.slug)








