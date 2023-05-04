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
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
def csrf_failure(request,reason="Error Loading"):
    return redirect('home')
from django.utils.safestring import mark_safe
# from sastaMail.settings import USERNAME
# Create your views here.
#################################################################
#Firebase Module
#################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
def connection():
    cred = credentials.Certificate("user/serviceAccountKey.json")
    try:
        firebase_admin.initialize_app(cred)
        # firebase_admin.initialize_app(cred,name=dt.now().strftime('%d%m%y%H%M%S'))
    except:
        firebase_admin.initialize_app(cred,name=dt.now().strftime('%d%m%y%H%M%S%f'))

def insertKey(username,publicKey):
    connection()
    myDB = firestore.client()
    data = {
        'publicKey':publicKey,
    }
    welcomeMessage = {
        'id':DT.now().strftime('%y%m%d%H%M%S%f'),
        'timeStamp':SERVER_TIMESTAMP,
        'subject':'Welcome',
        'message':'Welcome to QuikMail',
    }
    myDB.collection('usersDB').document(username).set(data)
    welcomeMessage['by']='TeamTechPhantoms'
    myDB.collection('usersDB').document(username).collection('inbox').add(welcomeMessage)
    del welcomeMessage['by']
    del welcomeMessage['id']
    del welcomeMessage['timeStamp']
    del welcomeMessage['subject']
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

import binascii

def keyGen(username):
    keyPair = RSA.generate(2048)
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
        sender = request.user.username
        senderData=myDB.collection('usersDB').document(sender).get()
        send_publicKey = senderData.to_dict()['publicKey']
        send_encryptor = PKCS1_OAEP.new(RSA.import_key(send_publicKey))
        send_encrypted = send_encryptor.encrypt(message)
        messageContent = {
            'id':DT.now().strftime('%y%m%d%H%M%S%f'),
            'timeStamp':SERVER_TIMESTAMP,
            'subject':subject,
            'message':encrypted,
            # 'sendMessage':send_encrypted,
        }
        # sender = request.user.username
        # senderData=myDB.collection('usersDB').document(sender).get()
        # send_publicKey = myData.to_dict()['publicKey']
        # send_encryptor = PKCS1_OAEP.new(RSA.import_key(send_publicKey))
        # send_encrypted = send_encryptor.encrypt(message)
        # sendMessageContent = {
        #     'id':DT.now().strftime('%y%m%d%H%M%S%f'),
        #     'timeStamp':SERVER_TIMESTAMP,
        #     'subject':subject,
        #     'message':send_encrypted,
        # }
        messageContent['by'] = sender
        myDB.collection('usersDB').document(reciever).collection('inbox').add(messageContent)
        del messageContent['by']
        del messageContent['message']
        messageContent['message']=send_encrypted
        messageContent['to'] = reciever
        myDB.collection('usersDB').document(sender).collection('outbox').add(messageContent)
        del messageContent['to']
        # messageContent['by'] = sender
        # myDB.collection('usersDB').document(reciever).collection('inbox').add(messageContent)
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
        temp['id'] = obj['id']
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
        temp['id'] = obj['id']
        context.append(temp)
    return context

def seeInbox(request,id):
    # print("ID IS ::",id)
    #test
    connection()
    myDB = firestore.client()
    myData = myDB.collection('usersDB').document(request.user.username).collection('inbox').where("id","==",id).get()
    myObject = list(myData)[0].to_dict()
    msg = myObject['message']
    myKey = myDB.collection('privateKeys').document(request.user.username).get()
    privateKey = myKey.to_dict()['privateKey']
    decryptor = PKCS1_OAEP.new(RSA.import_key(privateKey))
    try:
        newMsg = decryptor.decrypt(msg)
        newMsg = newMsg.decode('utf-8')
        messages.info(request,mark_safe(newMsg))
    except:
        messages.info(request,msg)
    return redirect('home')

def seeOutbox(request,id):
    connection()
    myDB= firestore.client()
    myData=myDB.collection('usersDB').document(request.user.username).collection('outbox').where("id","==",id).get()
    myObject= list(myData)[0].to_dict()
    msg=myObject['message']
    myKey=myDB.collection('privateKeys').document(request.user.username).get()
    privateKey = myKey.to_dict()['privateKey']
    decryptor = PKCS1_OAEP.new(RSA.import_key(privateKey))
    try:
        newMsg = decryptor.decrypt(msg)
        newMsg = newMsg.decode('utf-8')
        messages.warning(request,newMsg)
    except:
        messages.warning(request,msg)
    return redirect('home')

def logoutUser(request):
    logout(request)
    return redirect('home')
#################################################################
#Testing
#################################################################

