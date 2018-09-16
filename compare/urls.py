from django.urls import path
from . import views

app_name = 'compare'

urlpatterns = [
    path('', views.index, name='index'),
    path('forecast/<city_name>', views.forecast, name='forecast')
]