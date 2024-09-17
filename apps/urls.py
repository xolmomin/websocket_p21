from django.urls import path

from apps import views

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
# 10.10.2.48
]

# docker run --name postgres_container -e POSTGRES_PASSWORD=1 -p 5432:5432 -d postgres:alpine
