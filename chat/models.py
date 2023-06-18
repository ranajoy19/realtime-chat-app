from django.db import models
from django.contrib.auth.models import User ,AnonymousUser
from django.db.models import SET
# Create your models here.

class Message(models.Model):
    sender_user = models.ForeignKey(User,related_name='sender',on_delete=SET(AnonymousUser.id))
    receiver_user = models.ForeignKey(User,related_name='receiver',on_delete=SET(AnonymousUser.id))
    massage = models.TextField()
    timestamp =models.DateTimeField(auto_now_add=True)


class Room(models.Model):
    sender_user = models.ForeignKey(User,related_name='room_sender',on_delete=SET(AnonymousUser.id))
    receiver_user = models.ForeignKey(User,related_name='room_receiver',on_delete=SET(AnonymousUser.id))
    room_name = models.CharField(max_length=200,unique=True)

    def __str__(self) -> str:
        return self.room_name