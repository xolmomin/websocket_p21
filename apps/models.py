from django.db.models import Model, DateTimeField, TextField, ForeignKey, CASCADE, FileField, SET_NULL, OneToOneField
from django.db.models.functions import Now


class TimeBasedModel(Model):
    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True, db_default=Now())


class Attachment(TimeBasedModel):
    file = FileField(upload_to='attachments/%Y/%m/%d/')


class Message(Model):
    message = TextField(null=True, blank=True)
    file = OneToOneField('apps.Attachment', SET_NULL, null=True, blank=True)
    author = ForeignKey('auth.User', CASCADE, related_name='messages')
    created_at = DateTimeField(auto_now_add=True)
