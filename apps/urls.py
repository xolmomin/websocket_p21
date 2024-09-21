from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps import views
from apps.views import AttachmentCreateAPIView, AttachmentRetrieveAPIView

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('attachments', AttachmentCreateAPIView.as_view(), name="attachments"),
    path('attachments/<int:pk>', AttachmentRetrieveAPIView.as_view(), name="attachments-detail"),
    path('', views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
]
