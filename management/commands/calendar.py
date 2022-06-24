from django.core.management.base import BaseCommand, CommandError
from order.models import LoadModel
from django.db.models import Q
import datetime
from django.shortcuts import get_object_or_404, get_list_or_404
import Bikum.settings as settings
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials
from chat.models import TokenModel

class Command(BaseCommand):

    def handle(self, *args, **options):
        date = datetime.date.today() + datetime.timedelta(days=1)

        loads = LoadModel.objects.filter(Q(status="2"), Q(pickup_date=date) | Q(dropoff_date=date))
        self.stdout.write('number of loads "%s" ' % len(loads))
        users = []
        if len(loads) > 0:
            lookup_date = str(date).replace("-",",")
            for load in loads:
                if load.created_by not in users:
                    users += [load.created_by]
                if load.assigned_to not in users:
                    users += [load.assigned_to]
            counter = 0
            for user in users:
                if user is not None:
                    try:
                        tokens = TokenModel.objects.get(user_reg=user).value
                    except:
                        continue
                    else:
                        list_tokens = [token for token in tokens if token != ""]
                        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
                        print("number of items", len(firebase_admin._apps.items()))
                        link = f'https://bikum.org/chat/calendar_Loads_list/{lookup_date}'

                        if len(firebase_admin._apps.items()) == 0:
                            default_app = firebase_admin.initialize_app(cred)
                        title = "Calendar notification"
                        body = f'Check your loads for tomorrow {date}'
                        message = messaging.MulticastMessage(
                            notification=messaging.Notification(title=title, body=body),
                            webpush=messaging.WebpushConfig(
                                notification=messaging.WebpushNotification(icon='/media/home/logo.png'),
                                fcm_options=messaging.WebpushFCMOptions(
                                    link=link)),
                            tokens=list_tokens)
                        response = messaging.send_multicast(message)
                        counter += 1
                self.stdout.write(self.style.SUCCESS('Successfully sending notifications to "%s" users' % counter))
                self.stdout.write('List of users: "%s" ' % users)
                self.stdout.write('louckup date: "%s" ' % lookup_date)
        else:
            raise CommandError('There is no loads in "%s' % date)


