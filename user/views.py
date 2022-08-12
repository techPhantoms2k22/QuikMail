from unittest import result
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
from datetime import datetime as DT
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

def keyGen(username):
    keyPair = RSA.generate(1024)
    pubKey = keyPair.publickey()
    keyPair = keyPair.exportKey()
    # keyN = hex(pubKey.n)
    # keyE = hex(pubKey.e)
    # keyD = hex(keyPair.d)
    # data = userDB(username=username,first_name=first_name,last_name=last_name,password=password)
    # data.save()
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
                keyGen(userid)
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
@login_required(login_url='home')
def dashboard(request):
    if request.method == "POST":
        reciever = request.POST['to']
        subject = request.POST['sub']
        message = request.POST['msg']
        #Firebase Connection
        connection()
        myDB = firestore.client()
        #Encryption
        myData = myDB.collection('usersDB').document(reciever).get()
        try:
            publicKey = myData.to_dict()['publicKey']
        except:
            messages.error(request,"Username Invalid.")
            return redirect('dashboard')
        message = bytes(message,'utf-8')
        encryptor = PKCS1_OAEP.new(RSA.import_key(publicKey))
        encrypted = encryptor.encrypt(message)
        messageContent = {
            'timeStamp':DT.now(),
            'subject':subject,
            'message':encrypted,
        }
        sender = request.user.username
        messageContent['to'] = reciever
        myDB.collection('usersDB').document(sender).collection('outbox').add(messageContent)
        del messageContent['to']
        messageContent['by'] = sender
        myDB.collection('usersDB').document(reciever).collection('inbox').add(messageContent)
        messages.success(request,"Message Successfully Sent.")
        return redirect('home')
    incoming = incomingMessages(request.user.username)
    outgoing = outgoingMessages(request.user.username)
    context = {
                'incoming':incoming,
                'outgoing':outgoing,
            }
    return render(request,'user/index.html',context)

def incomingMessages(userName):
    connection()
    myFireStore = firestore.client()
    queryObj = myFireStore.collection('usersDB').document(userName).collection('inbox')
    results = queryObj.order_by('timeStamp',direction = firestore.Query.DESCENDING)
    ovlResults = list(results.stream())
    context = list()
    for each in ovlResults:
        temp = dict()
        obj = each.to_dict()
        temp['by'] = obj['by']
        temp['subject'] = obj['subject']
        context.append(temp)
    return context

def outgoingMessages(userName):
    connection()
    myFireStore = firestore.client()
    queryObj = myFireStore.collection('usersDB').document(userName).collection('outbox')
    results = queryObj.order_by('timeStamp',direction = firestore.Query.DESCENDING)
    ovlResults = list(results.stream())
    context = list()
    for each in ovlResults:
        temp = dict()
        obj = each.to_dict()
        temp['to'] = obj['to']
        temp['subject'] = obj['subject']
        context.append(temp)
    return context

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
