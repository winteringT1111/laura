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
    path('attendance/', views.attendance, name='attendance'),
    # 조사
    path('search/', views.search, name='search'),
    path('search/create', views.search_create, name='search'),
    # 수업
    path('class/', views.class_main, name='class'),
    path('class/herbology', views.herb, name='herb'),
    path('class/creature', views.creature, name='creature'),
    path('class/flying', views.shifter, name='shifter'),
    path('class/teleport', views.teleport, name='teleport'),
    path('class/potion/', views.potion, name='potion'),
    path('check_combination/', views.check_combination, name='check_combination'),
    
    path('test/', views.story_view, name='story_view'),
    path("room/<str:room_name>/", views.room, name="room"),
] 

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
