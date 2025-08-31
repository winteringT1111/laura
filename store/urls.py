from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('store/', views.store_main, name='store_main'),
]