from django.http import HttpResponse
from django.shortcuts import redirect, render
from datetime import datetime as dt
import user
from user.models import userDB
from .forms import NewUserForm
from django.contrib.auth import login , authenticate , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password , check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.csrf import csrf_failure
from django.contrib.auth.decorators import login_required
def csrf_failure(request,reason="Error Loading"):
    return redirect('home')
# from sastaMail.settings import USERNAME
# Create your views here.
#################################################################
#Firebase Module
#################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
def connection():
    cred = credentials.Certificate("user/serviceAccountKey.json")
    try:
        firebase_admin.initialize_app(cred)
        firebase_admin.initialize_app(cred,name=dt.now().strftime('%d%m%y%H%M%S'))
    except:
        firebase_admin.initialize_app(cred,name=dt.now().strftime('%d%m%y%H%M%S'))

def insertKey(username,publicKey):
    connection()
    myDB = firestore.client()
    data = {
        'publicKey':publicKey,
    }
    welcomeMessage = {
        'message':'Welcome to QuikMail',
    }
    myDB.collection('usersDB').document(username).set(data)
    myDB.collection('usersDB').document(username).collection('inbox').add(welcomeMessage)
    myDB.collection('usersDB').document(username).collection('outbox').add(welcomeMessage)

def privateKey(username,private_key):
    connection()
    myDB = firestore.client()
    key = {
        'privateKey':private_key,
    }
    myDB.collection('privateKeys').document(username).set(key)
##################################################################
#End Module
##################################################################
#################################################################
#Cryptography
#################################################################
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP ,PKCS1_v1_5
import binascii

def keyGen(username,first_name,last_name,password):
    keyPair = RSA.generate(1024)
    pubKey = keyPair.publickey()
    keyPair = keyPair.exportKey()
    # keyN = hex(pubKey.n)
    # keyE = hex(pubKey.e)
    # keyD = hex(keyPair.d)
    data = userDB(username=username,first_name=first_name,last_name=last_name,password=password)
    data.save()
    insertKey(username,pubKey.exportKey())
    privateKey(username,keyPair)
#################################################################
#End
#################################################################
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        if request.POST.get('fname') and request.POST.get('lname'):
            fname = request.POST['fname']
            lname = request.POST['lname']
            userid = request.POST['uID']
            password = request.POST['psw']
            try:
                checkUser = User.objects.get(username = userid)
                messages.error(request,"Username Exists")
            except:
                user = User.objects.create_user(username = userid,email = None,password = password)
                user.first_name = fname
                user.last_name = lname
                user.save()
                messages.success(request,"Account Created")
        elif request.POST.get('uname'):
            userName = request.POST['uname']
            userPassword = request.POST['password']
            user = authenticate(request,username = userName,password = userPassword)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.error(request,"Username , Password does not exists")
        else:
            return HttpResponse("ERROR")
    return render(request,'user/home.html')

import json
def dashboard(request):
    if request.POST.get('userName'):
        name = request.POST.get('userName')
        print("hello ")
        print(name)
    else:
        print("BAL")
    return render(request,'user/dashboard.html')

def logoutUser(request):
    logout(request)
    return redirect('home')
#################################################################
#Testing
#################################################################
def test(request):
    if request.method == "POST":
        sender = request.POST['send']
        message = request.POST['message']
        reciv = request.POST['recv']
        # messageContent = {
        #     'message':message,
        # }
        connection()
        myDB = firestore.client()
        #encryption
        myData = myDB.collection('usersDB').document(reciv).get()
        publicKey = myData.to_dict()['publicKey']
        message = bytes(message,'utf-8')
        encryptor = PKCS1_OAEP.new(RSA.import_key(publicKey))
        encrypted = encryptor.encrypt(message)
        messageContent = {
            'message':encrypted,
        }
        myDB.collection('usersDB').document(sender).collection('outbox').add(messageContent)
        myDB.collection('usersDB').document(reciv).collection('inbox').add(messageContent)
        # print("**************",type(publicKey))
    return render(request,'user/message.html')

def test1(request):
    connection()
    myDB = firestore.client()
    myData = myDB.collection('usersDB').document('mclovin').collection('inbox').document('ZltdespKEV6iuuFYDjuD').get()
    msg = myData.to_dict()['message']
    myKey = myDB.collection('privateKeys').document('mclovin').get()
    privateKey = myKey.to_dict()['privateKey']
    decryptor = PKCS1_OAEP.new(RSA.import_key(privateKey))
    newMsg = decryptor.decrypt(msg)
    return HttpResponse(newMsg)
