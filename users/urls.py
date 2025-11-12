from django.urls import path
from users import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='users_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='users_signup'),
    path('dungeon1/b1/', views.dungeon_b1_view, name='dungeon1_b1_view'),
    path('dungeon1/b1/submit/', views.create_dungeon_log_view, name='create_dungeon_log'),
    path('dungeon1/b3/', views.dungeon_b3_view, name='dungeon_b3_view'),
    path('dungeon1/b3/submit/', views.create_dungeon_log_b3_view, name='create_dungeon_log_b3'),
    path('dungeon/drakus-b1/', views.dungeon_b1_drakus_view, name='dungeon_b1_drakus_view'),
    path('dungeon/drakus-b1/submit/', views.create_dungeon_log_drakus_view, name='create_dungeon_log_drakus'),
    path('dungeon/drakus-b3/', views.dungeon_b3_drakus_view, name='dungeon_b3_drakus_view'),
path('dungeon/drakus-b3/submit/', views.create_dungeon_log_drakus_b3_view, name='create_dungeon_log_drakus_b3'),
]   