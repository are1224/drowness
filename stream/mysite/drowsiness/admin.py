from django.contrib import admin
from .models import User_info, TTS_text, Eye_threshold

# Register your models here.

admin.site.register(User_info)
admin.site.register(TTS_text)
admin.site.register(Eye_threshold)