from django.shortcuts import render, redirect
from django.http import HttpResponse
import drow.tts as TTS
from django.http import FileResponse
from django.conf import settings
import os, mimetypes
from .models import Sound, User_info
from .models import TTS_text
from django.contrib.auth.models import User
from django.contrib.auth import authenticate 
import django.contrib.auth as auth

import json

import echo.mytube as mytube
from django.views.decorators.csrf import csrf_exempt

# Create your views here. 

#Web Cam Streaming

def alarm(request, user_pk): # 알람을 확인하는 부분
    if request.method == 'GET':
        # print(settings.BASE_DIR)

        user = User.objects.get(pk=user_pk)

        context = {
            'results' : user.streamer.tts
        }

        return render(request, 'alarm.html',context)

def room(request, room_name): # get 요청으로 웹캠 스트리밍을 시작하기 위한 처리.
    return render(request, 'chat/room.html',{
        'room_name':room_name
    })

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#authentication

ERROR_MSG = {
    'ID_EXIST': '이미 사용 중인 아이디 입니다.',
    'ID_NOT_EXIST': '존재하지 않는 아이디 입니다.',
    'ID_PW_MISSING': '아이디와 비밀번호를 확인해주세요.',
    'PW_CHECK': '비밀번호가 일치하지 않습니다.'
}

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':

        context = {
            'error':{
                'state':False,
                'msg':''
            }
        }

        error_msg = {
            'ID_EXIST' : '이미 사용 중인 아이디 입니다.',
            'ID_NOT_EXIST' : '존재하지 않는 아이디 입니다.',
            'ID_PW_MISSING' : '아이디와 비밀번호를 다시 확인해주세요.',
            'PW_CHECK' : '비밀번호가 일치하지 않습니다.'
        }

        userid = request.POST['id']
        pwd = request.POST['pwd']
        re_pwd = request.POST['pwd_re']
        email = request.POST['email']

        #추가
        name = request.POST['name']

        user = User.objects.filter(username=userid)

        if userid and pwd:

            if len(user)==0: #쿼리 객체가 배열로 리턴 된다.
                #아이디가 디비 안에 없다.

                if (pwd==re_pwd):

                    user = User.objects.create_user(
                        username=userid,
                        password=pwd
                    )

                    #추가 
                    User_info.objects.create(
                        user = user,
                        name = name,
                        mail = email
                    )

                    auth.login(request,user)

                    return redirect('tts', user.pk)

                else:
                    context['error']['state'] = True
                    context['error']['msg'] = error_msg['PW_CHECK']
            else:
                context['error']['state'] = True
                context['error']['msg'] = error_msg['ID_EXIST']

        else:
            context['error']['state'] = True
            context['error']['msg'] = error_msg['ID_PW_MISSING']
            

        return render(request, 'signup.html', context)


    elif request.method == 'GET':
        return render(request, 'signup.html')


    return render(request, 'signup.html', context)

def about(request):
    return render(request, 'about.html')

def login(request):
    if request.method == 'POST':

        error_msg = {
            'not_input_id_or_pwd' : '아이디 혹은 비밀번호를 입력해주세요.',
            'not_id':'사용자가 입력하신 아이디는 존재하지 않습니다.',
            'not_match_pwd':'비밀번호가 일치하지 않습니다.'
        }

        context = {
            'error':{
                'state':False,
                'msg':''
            }
        }

        userid = request.POST['id']
        pwd = request.POST['pwd']

        user = User.objects.filter(username=userid)

        if (userid and pwd):

            if len(user)!=0 :
                
                user = auth.authenticate(
                    username=userid,
                    password=pwd
                )

                if user != None:
                    auth.login(request, user)

                    # return redirect('tts', user.pk)
                    if user.streamer.tts.text == '':
                        return redirect('tts', user.pk)
                    else:
                        # print(user.streamer.tts.text)
                        return redirect('../stream/green/')

                else :
                    context['error']['state'] = True
                    context['error']['msg'] = error_msg['not_match_pwd']

            else:
                context['error']['state'] = True
                context['error']['msg'] = error_msg['not_id']

        else:
            context['error']['state'] = True
            context['error']['msg'] = error_msg['not_input_id_or_pwd']

        return render(request, 'login.html', context) 

    elif request.method == 'GET':
        return render(request, 'login.html')   

def logout(request):
    auth.logout(request)

    return redirect('home')

def eye(request):
    return render(request, 'eye.html')

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# for tts

def tts(request, user_pk):

    if request.method == 'POST':

        # 데이터베이스에 추가하기
        
        # print(user_pk)
        
        content = request.POST['text']
        name = TTS.make_tts(content)

        user = User.objects.get(pk=user_pk)

        TTS_text.objects.create(
            text=name,
            user_info = user.streamer
        )

        return redirect('../stream/green/')

    else : return render(request, 'tts.html', {'user_pk':user_pk})

def change_tts(request, user_pk):

    user = User.objects.get(pk=user_pk)
    text = user.streamer.tts.text

    content = request.POST['text']

    name = TTS.change_tts(text, content)

    tts_val = TTS_text.objects.filter(text = text)
    tts_val.update(
            text = name
        )

    return HttpResponse(name)


def get_tts_url(request):
    
    user_pk = request.POST.get('pk', None)
    print(user_pk)
    user = User.objects.get(pk=int(user_pk))
    context = {
        'tts_url': user.streamer.tts.text
    }

    return HttpResponse(json.dumps(context), content_type="application/json")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@csrf_exempt 
def get_url(request):
    title = request.POST.get('title', None)
    singer = request.POST.get('singer', None)

    text = str(title)+' '+str(singer)+' karaoke'
    print(text)
    context = {
        'result' : mytube.get_url(text)
    }

    return HttpResponse(json.dumps(context), content_type="application/json")





