"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drowsiness import views
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #home
    path('home', views.home, name='home'),
    #모델 관리
    path('admin/', admin.site.urls),
    # 웹캠 스트리밍이 이루어지는 path
    path('stream/', include('drowsiness.urls')),
    # 알람을 설정하는 path
    path('alarm/<int:user_pk>', views.alarm, name='alarm'),
    # authentication
    path('signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # tts 설정
    path('tts/<int:user_pk>', views.tts, name='tts'),
    path('signup/eye/', views.eye, name='eye'),
    # tts 교체
    path('change_tts/<int:user_pk>', views.change_tts, name='change_tts'),
    # tts url 얻기
    path('get_tts_url/', views.get_tts_url, name='get_tts_url'),
    path('get_url', views.get_url, name='get_url')
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
