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

    path('world/realm/novarium', views.novarium, name='novarium'),
    path('world/realm/belisar', views.belisar, name='belisar'),
    path('world/realm/zerka', views.zerka, name='zerka'),
    path('world/realm/tarvel', views.tarvel, name='tarvel'),
    path('world/realm/elysion', views.elysion, name='elysion'),
    path('world/realm/cardin', views.cardin, name='cardin'),
    path('world/realm/drakus', views.drakus, name='drakus'),
    path('world/realm/necros', views.necros, name='necros'),
    path('world/realm/serapium', views.serapium, name='serapium'),
    

    path('attendance/', views.attendance, name='attendance'),
    # 조사
    path('search/', views.search, name='search'),
    path('search/create', views.search_create, name='search'),
    # 수업
    path('class/', views.class_main, name='class'),
    path('class/herbology', views.herb, name='herb'),

    path('check_combination/', views.check_combination, name='check_combination'),
    
    path('test/', views.story_view, name='story_view'),
    path("room/<str:room_name>/", views.room, name="room"),
] 

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
