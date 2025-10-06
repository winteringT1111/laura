from django.urls import path
from member import views

app_name = 'member'

urlpatterns = [
    path('member', views.member_main, name='member_main'),
    path('member/<str:charEngName>', views.member_profile, name='member_profile'),
    path('use_fortune_cookie/', views.use_fortune_cookie, name='use_fortune_cookie'),
    path('transfer_item/', views.transfer_item, name='transfer_item'),
    path('giftbox', views.giftbox, name='giftbox'),
]