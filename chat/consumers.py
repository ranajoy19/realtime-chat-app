# chat/consumers.py
import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        print("connected", self.room_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
            # Leave room group
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
            )
            print("disconnected", self.room_group_name)

    def save_message(self,message,sender,receiver):
        sender_user = User.objects.get(id=sender)
        receiver_user = User.objects.get(id=receiver)
        new_message = Message.objects.create(massage=message,
                                             sender_user=sender_user,receiver_user=receiver_user) 
        new_message.save()


    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender =text_data_json["sender"]
        receiver =text_data_json["receiver"]
        sender_name = text_data_json["sender_name"]
        self.save_message(message,sender,receiver)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {"type": "chat_message",
                    'message': message,
                    'sender':sender,
                    'receiver':receiver,
                    'sender_name':sender_name
                    }
        )



        # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        sender =event["sender"]
        receiver =event["receiver"]
        sender_name = event["sender_name"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message,
                                        'sender':sender,
                                        'receiver':receiver,
                                        'sender_name':sender_name,
                                        'time':f"{datetime.now().strftime('%I:%M %p')}"}
                                        ))