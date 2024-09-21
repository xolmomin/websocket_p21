from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from apps.models import Attachment
from apps.serializers import AttachmentModelSerializer, AttachmentDetailModelSerializer


class AttachmentCreateAPIView(CreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentModelSerializer


class AttachmentRetrieveAPIView(RetrieveAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentDetailModelSerializer


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
