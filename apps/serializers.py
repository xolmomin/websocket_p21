from rest_framework.serializers import ModelSerializer

from apps.models import Attachment


class AttachmentModelSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = 'id', 'file'

        extra_kwargs = {
            'file': {'write_only': True},
        }


class AttachmentDetailModelSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
