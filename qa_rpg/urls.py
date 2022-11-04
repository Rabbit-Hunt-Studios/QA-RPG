from django.urls import path

from . import views

app_name = 'qa_rpg'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('template/', views.TemplateView.as_view(), name='template'),
    path('template/summon/', views.SummonView.as_view(), name='summon'),
    path('template/summon/create', views.create, name='create'),
    path('dungeon/', views.DungeonView.as_view(), name='dungeon'),
    path('dungeon/action', views.action, name='action'),
    path('dungeon/battle', views.BattleView.as_view(), name='battle'),
    path('dungeon/battle/check/<int:question_id>', views.check, name='check'),
    path('dungeon/treasure', views.TreasureView.as_view(), name='treasure'),
    path('dungeon/treasure/treasure_action', views.treasure_action, name='treasure_action'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/claim/<int:question_id>', views.claim_coin, name='claim'),
    path('', views.HomeView.as_view(), name='home')
]
