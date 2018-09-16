from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from accounts.models import UserInfo
from compare.weather import query_api

class Command(BaseCommand):
    """Searches all users in db and emails them current weather of last known location"""
    def handle(self, *args, **options):
        users = User.objects.all()
        for u in users:
            info = UserInfo.objects.get(user=u)
            location = info.current_city
            if location:
                resp = query_api(location)
                if resp and resp['cod'] != '404':
                    temperature = resp['main']['temp']
                    wind = resp['wind']['speed']
                    message = """Weather in """+location+""" 
                        Temperature - """+str(temperature)+"""
                        Windspeed - """+str(wind)+""" m/s
                    """
                    email = EmailMessage('Weather of the day for '+location, message, to=[u.email])
                    email.send()