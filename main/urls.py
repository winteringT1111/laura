from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('notice', views.notice, name='notice'),
    path('world', views.world, name='world'),
    path('system', views.system, name='system'),
    path('world/species', views.species, name='species'),
    path('world/war', views.war, name='war'),
    path('world/realm', views.realm, name='realm'),
    path('world/story', views.worldstory, name='worldstory'),

    path('world/realm/novarium', views.novarium, name='novarium'),
    path('world/realm/belisar', views.belisar, name='belisar'),
    path('world/realm/zerka', views.zerka, name='zerka'),
    path('world/realm/tarvel', views.tarvel, name='tarvel'),
    path('world/realm/elysion', views.elysion, name='elysion'),
    path('world/realm/cardin', views.cardin, name='cardin'),
    path('world/realm/drakus', views.drakus, name='drakus'),
    path('world/realm/necros', views.necros, name='necros'),
    path('world/realm/serapium', views.serapium, name='serapium'),
    

    path('supply/', views.supply, name='supply'),
    # 수업
    path('class/herbology', views.herb, name='herb'),

    path('recipe/', views.recipe, name='recipe'),
    path('combine/', views.combine, name='combine'),
    
    path('story/<str:room_name>/', views.story_view, name='story_view'),
    path("room/", views.room, name="room"),
    path('room/claim_reward/', views.claim_story_reward, name='claim_story_reward'),

    # 일일 퀘스트
    path('quests/', views.quest_board, name='quest_board'),
    path('quests/submit/', views.create_quest_log, name='create_quest_log'),
] 

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
