
import requests
import xml.etree.ElementTree as ET 
import tempfile
import datetime
import os

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def indent(elem, level=0): 
    i = "\n" + level*" " 
    if len(elem): 
        if not elem.text or not elem.text.strip(): 
            elem.text = i + " " 
        if not elem.tail or not elem.tail.strip(): 
            elem.tail = i 
        for elem in elem: 
            indent(elem, level+1) 
        if not elem.tail or not elem.tail.strip(): 
            elem.tail = i 
    else: 
        if level and (not elem.tail or not elem.tail.strip()): 
            elem.tail = i 

def make_tts(content):
    speak = ET.Element("speak") 
    voice1 = ET.Element("voice", name="WOMAN_READ_CALM") 
    voice1.text = content
    speak.append(voice1)  

    indent(speak) 
    ET.dump(speak)

    ET.ElementTree(speak).write("data.xml", encoding="utf-8", xml_declaration=True)



    kakao_tts_url = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
    rest_api_key = "0238684eeaa7b043ef3d0e011ad3caab"

    headers = {
        "Content-Type": "application/xml",
        "Authorization": "KakaoAK " + rest_api_key,
    }

    with open('data.xml', 'rb') as fp:
        data = fp.read()
    res = requests.post(kakao_tts_url, headers=headers, data = data)
    rescode = int(res.status_code)

    if(rescode==200):

        print("TTS mp3 저장")
        response_body = res.content

        basename = "alarm"
        folder = datetime.datetime.now().strftime("%y%m%d")
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix])

        createFolder('upload_files/{}'.format(folder))

        with open('upload_files/{0}/{1}.mp3'.format(folder, filename), 'wb') as f:
            f.write(response_body)

        return 'upload_files/{0}/{1}.mp3'.format(folder, filename)
    else:
        print(rescode)
        return None

def change_tts(text, content):

    try:
        os.remove(text)
    except Exception as ex:
        print('Exception : ',ex)
         
    speak = ET.Element("speak") 
    voice1 = ET.Element("voice", name="WOMAN_READ_CALM") 
    voice1.text = content
    speak.append(voice1)  

    indent(speak) 
    ET.dump(speak)

    ET.ElementTree(speak).write("data.xml", encoding="utf-8", xml_declaration=True)



    kakao_tts_url = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
    rest_api_key = "0238684eeaa7b043ef3d0e011ad3caab"

    headers = {
        "Content-Type": "application/xml",
        "Authorization": "KakaoAK " + rest_api_key,
    }

    with open('data.xml', 'rb') as fp:
        data = fp.read()
    res = requests.post(kakao_tts_url, headers=headers, data = data)
    rescode = int(res.status_code)

    if(rescode==200):

        print("TTS mp3 저장")
        response_body = res.content

        basename = "alarm"
        folder = datetime.datetime.now().strftime("%y%m%d")
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix])

        createFolder('upload_files/{}'.format(folder))

        with open('upload_files/{0}/{1}.mp3'.format(folder, filename), 'wb') as f:
            f.write(response_body)

        return 'upload_files/{0}/{1}.mp3'.format(folder, filename)
    else:
        print(rescode)
        return None

    