from django.db.models import Model, DateTimeField


class Message(Model):
    created_at = DateTimeField(auto_now_add=True)
