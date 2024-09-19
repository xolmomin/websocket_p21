from django.db.models import Model, DateTimeField, TextField, ForeignKey, CASCADE


class Message(Model):
    message = TextField()
    author = ForeignKey('auth.User', CASCADE, related_name='messages')
    created_at = DateTimeField(auto_now_add=True)
