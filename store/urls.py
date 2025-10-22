from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('store/', views.store_main, name='store_main'),
    path('fishing/', views.fishing_spot, name='fishing_spot'),
    path('fishing/cast/', views.cast_rod, name='cast_rod'),
    path('fishing/create/', views.create_fishing_log_page, name='create_fishing_log_page'),
]