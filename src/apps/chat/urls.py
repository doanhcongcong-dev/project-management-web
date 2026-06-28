from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.room_list, name='list'),
    path('room/<int:pk>/', views.room_detail, name='detail'),
    path('room/create/', views.create_room, name='create_room'),
]