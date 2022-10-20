from django.urls import path

from . import views

app_name = 'qa_rpg'
urlpatterns = [
    path('', views.index, name='index'),
]