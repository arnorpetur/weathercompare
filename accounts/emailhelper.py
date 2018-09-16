from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.auth.models import User


def email_logged(user):
    has_email = False
    current_user = User.objects.get(username = user)
    if current_user.email:
        has_email = True
    return has_email

def get_location(request):
    g = GeoIP2('geoip')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print(ip)

    return g.city('205.186.163.125')['city']