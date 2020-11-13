from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import cv2
import threading
import base64
from drow.drowsiness_detector import Drowsiness
import time

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.camera = None
        self.thread = None
        print('hello')
    
    def disconnect(self, close_code):

        print('good bye')
        try:
            if self.camera:
                (self.camera).stop()
                del self.camera
                self.camera = None
        except Exception as ex:
            print('i got it!😆', ex)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        message = text_data_json['message']
        print('look at this : ',message)

        if message != 'stop':
            self.camera = Drowsiness(message)
            self.thread = threading.Thread(target=self.circle, args=())
            self.thread.daemon = True
            self.thread.start()

        else:
            try:
                if self.camera:
                    (self.camera).stop()
                    del self.camera
                    self.camera = None
            except Exception as ex:
                print('ended 🎶', ex)

    def circle(self):
        time.sleep(2)
        
        while self.camera is not None:
            try:
                if self.camera.check:
                    
                    frame = (self.camera).get_frame()
                    self.send(bytes_data=frame)
            except Exception as ex:
                print('done😍', ex)
                break