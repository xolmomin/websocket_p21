from django.contrib.auth.models import User
from django.db.models import Model, DateTimeField, ForeignKey, CASCADE, FileField, CharField, ManyToManyField, \
    SlugField, BooleanField
from django.db.models.functions import Now


class TimeBasedModel(Model):
    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        abstract = True


class SlugBasedModel(Model):
    title = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class DeleteBasedModel(Model):
    is_deleted = BooleanField(db_default=False)

    class Meta:
        abstract = True


class Attachment(TimeBasedModel):
    file = FileField(upload_to='attachments/%Y/%m/%d/')


class Room(Model):
    name = CharField(max_length=128)
    online = ManyToManyField('auth.User', blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'


class Message(TimeBasedModel):
    user = ForeignKey('auth.User', CASCADE)
    room = ForeignKey('apps.Room', CASCADE)
    text = CharField(max_length=512)

    def __str__(self):
        return f'{self.user.username}: {self.text} [{self.created_at}]'
