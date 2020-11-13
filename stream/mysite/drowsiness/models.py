from django.db import models
from django.contrib.auth.models import User

class Sound(models.Model) :
    title = models.CharField(max_length=100)
    alarm = models.FileField(upload_to="./sound", blank=True)

class User_info(models.Model):
    objects=models.Manager()

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='streamer'
    )

    name=models.CharField(max_length=20)
    mail=models.CharField(max_length=20)

class TTS_text(models.Model):
    objects=models.Manager()
    text=models.TextField()
    user_info = models.OneToOneField(
        User_info, on_delete=models.CASCADE, related_name='tts'
    )

class Eye_threshold(models.Model):
    objects=models.Manager()
    eye_info=models.FloatField()
    user_info = models.OneToOneField(
        User_info, on_delete=models.CASCADE, related_name='eye_threshold'
    )




