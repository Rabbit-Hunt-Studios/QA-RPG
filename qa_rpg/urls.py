from django.urls import path

from . import views

app_name = 'qa_rpg'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('dungeon/', views.DungeonView.as_view(), name='dungeon'),
    path('dungeon/action', views.action, name='action'),
    path('dungeon/battle', views.BattleView.as_view(), name='battle'),
    path('dungeon/battle/check/<int:question_id>', views.check, name='check')
]
