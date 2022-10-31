from django.urls import path

from . import views

app_name = 'qa_rpg'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('summon/', views.SummonView.as_view(), name='summon'),
    path('summon/create', views.create, name='create'),
    path('dungeon/', views.DungeonView.as_view(), name='dungeon'),
    path('dungeon/action', views.action, name='action'),
    path('dungeon/battle', views.BattleView.as_view(), name='battle'),
    path('dungeon/battle/check/<int:question_id>', views.check, name='check'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/claim/<int:question_id>', views.claim_coin, name='claim'),
    path('home/', views.HomeView.as_view(), name='home' )
]
