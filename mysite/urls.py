"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from .views import signup, custom_login, custom_logout,policy

urlpatterns = [
    path('qa_rpg/', include('qa_rpg.urls')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='qa_rpg/')), 
    path("__reload__/", include("django_browser_reload.urls")),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('signup/', signup, name='signup'),
    path('accounts/login/', custom_login, name='login'),
    path('policy/', policy, name='policy')
]
