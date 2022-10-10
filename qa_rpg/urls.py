from django.urls import path

from . import views

app_name = 'qa-rpg'
urlpatterns = [
    path('', views.index, name='index'),
]