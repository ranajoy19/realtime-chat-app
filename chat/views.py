from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.views import View
from .models import Room,Message

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

# Create your views here.



#################### index#######################################
def index(request):
    return render(request, 'user/index.html', {'title':'index'})
  
########### register here #####################################
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            ##################################################################
            messages.success(
                request,
                'Your account has been created ! You are now able to log in',
            )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title':'register here'})
  
################ login forms###################################################
def Login(request):
    if request.method == 'POST':
      
        # AuthenticationForm_can_also_be_used__

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('rooms')
        else:
            messages.info(request, 'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form':form, 'title':'log in'})




class GetAllUsers(LoginRequiredMixin,View):
    def get(self,request):
        try:

        
            """
            get the all user from the database
            """
            users =User.objects.exclude(id=request.user.id)

            return render(request,'chat/all_users.html',{"users":users}  )
        except BaseException as E:
            print("e",E)
    def post(self,request):
        try:
            print("inside")
            """
            get the sender and receiver users and connect them with each othres respective rooms
            
            """
            sender = request.user.id
            receiver = request.POST['users']
            sender_user = User.objects.get(id=sender)
            receiver_user = User.objects.get(id=receiver)
            """
                Setting the receiver_user as a session veriable
            """
            request.session['receiver_user']=receiver

            # check if the sender and receiver already have a room

            get_room = Room.objects.filter(Q(sender_user=sender_user,receiver_user=receiver_user)|
                                        Q(sender_user=receiver_user,receiver_user=sender_user))
            print("get_room",get_room)


            # fetch the room if already exist

            if get_room:
                room_name =get_room[0].room_name
            else:
                # create a new room if room doesn't exist

                new_room = get_random_string(10)
                while True:
                    room_exist = Room.objects.filter(room_name=new_room)
                    if room_exist:
                        new_room = get_random_string(10)
                    else:
                        break

                create_room = Room.objects.create(sender_user=sender_user,receiver_user=receiver_user,
                                                room_name=new_room)
                create_room.save()
                room_name =create_room.room_name

            return redirect('room',room_name=room_name)

        except BaseException as e:
            print("eee",e)
class ChatRoom(LoginRequiredMixin, View):
    queryset = Room.objects.all()

    def get(self, request, room_name, *args, **kwargs):
        get_object_or_404(Room, room_name=self.kwargs.get("room_name"))
        room = Room.objects.get(room_name=self.kwargs.get("room_name"))
        sender = request.user.id

        sender_name = User.objects.get(id=sender).username
        # sets up the user as sender user for chatting
        if room.receiver_user.id == sender:
            receiver = room.sender_user.id
        else:
            receiver = room.receiver_user.id


        # get all the previous messages from the database
        messages = Message.objects.filter (Q(sender_user=sender,
        receiver_user=receiver) | Q(sender_user=receiver,receiver_user=sender)).order_by('timestamp')
        # print(messages[0].timestamp.strftime("%X"))
        return render (request, "chat/room.html", {
            'room_name':room_name,
            'sender_id': sender,
            'receiver_id': receiver,
            "messages": messages,
            "sender_name": sender_name
        })