from unittest import result
from django.http import HttpResponse
from django.shortcuts import redirect, render
from datetime import datetime as dt
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
#################################################################
#Firebase Module
#################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
import pyrebase
# Firebase NoSQL Database Connection Setup
def firebaseDatabaseConnection():
    # Creating a Access Certificate
    cred = credentials.Certificate("user/serviceAccountKey.json")
    # Creating an instance
    try:
        firebase_admin.initialize_app(cred)
    except:
        firebase_admin.initialize_app(cred,name=dt.now().strftime('%d%m%y%H%M%S%f'))

# Firebase Storage Bucket Connection Setup
from . import storageCredentials
def firebaseStorageConnection():
    # Creating Configurations
    firebaseConfigdefault = {
                        'apiKey': storageCredentials.apiKey,
                        'authDomain': storageCredentials.authDomain,
                        'projectId': storageCredentials.projectId,
                        'storageBucket': storageCredentials.storageBucket,
                        'messagingSenderId': storageCredentials.messagingSenderId,
                        'databaseURL' : storageCredentials.databaseURL,
                        'appId': storageCredentials.appId,
                        'measurementId': storageCredentials.measurementId,
    }
    # Setting up the connection
    firebaseConnection = pyrebase.initialize_app(firebaseConfigdefault)
    return firebaseConnection

def insertKey(username,publicKey):
    firebaseDatabaseConnection()
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
    firebaseDatabaseConnection()
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
    insertKey(username,pubKey.exportKey())
    privateKey(username,keyPair)
#################################################################
#End
#################################################################
from .models import userDatabase
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        if request.POST.get('fname') and request.POST.get('lname'):
            fname = request.POST['fname']
            lname = request.POST['lname']
            userid = request.POST['uID']
            password = request.POST['psw']
            dateOfBirth = request.POST['dob']
            phoneNumber = request.POST['phone']
            try:
                checkUser = User.objects.get(username = userid)
                messages.error(request,"Username Exists")
            except:
                user = User.objects.create_user(username = userid,email = None,password = password)
                user.first_name = fname
                user.last_name = lname
                user.save()
                keyGen(userid)
                userData = userDatabase(username = userid , firstName = fname , lastName = lname,dateOfBirth = dateOfBirth,phoneNumber = phoneNumber)
                userData.save()
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
import re
@login_required(login_url='home')
def dashboard(request):
    if request.method == "POST":
        reciever = request.POST['to']
        subject = request.POST['sub']
        message = request.POST['msg']
        #Accept the files from frontend
        files = request.FILES.getlist('attachment')
        if len(files) == 0:
            attachment = False
        else:
            attachment = True
        #Firebase Connection
        firebaseDatabaseConnection()
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

        #Sending attachment
        attachmentList = [] # Keeping files list
        typeList = [] # Keeping extension list
        firebaseStorageConnectionObject = firebaseStorageConnection().storage()
        fileCount = 0
        #For NO ATTACHMENT
        extension = ""
        for file in files:
            extension = re.findall("(\\.[^.]+)$", str(file))[0]
            typeList.append(extension)
            fileCount += 1
            filename = DT.now().strftime('%y%m%d%H%M%S%f') + str(fileCount) + extension
            firebaseStorageConnectionObject.child(filename).put(file)
            fileURL = firebaseStorageConnectionObject.child(filename).get_url(None)
            attachmentList.append(fileURL)

        messageContent = {
            'id' : DT.now().strftime('%y%m%d%H%M%S%f'),
            'timeStamp' : SERVER_TIMESTAMP,
            'subject' : subject,
            'message' : encrypted,
            'attachment' : attachment,
            'attachmentArray' : attachmentList,
            'attachmentType':extension,
            'extensionList':typeList,
        }
        messageContent['by'] = sender
        myDB.collection('usersDB').document(reciever).collection('inbox').add(messageContent)
        del messageContent['by']
        del messageContent['message']
        messageContent['message']=send_encrypted
        messageContent['to'] = reciever
        # messageContent['attachmentArray'] = attachmentList
        myDB.collection('usersDB').document(sender).collection('outbox').add(messageContent)
        del messageContent['to']
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
    firebaseDatabaseConnection()
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
    firebaseDatabaseConnection()
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
    firebaseDatabaseConnection()
    myDB = firestore.client()
    myData = myDB.collection('usersDB').document(request.user.username).collection('inbox').where("id","==",id).get()
    myObject = list(myData)[0].to_dict()
    msg = myObject['message']
    ifAttachment = False
    try:
        ifAttachment = myObject['attachment']
    except:
        pass
    myKey = myDB.collection('privateKeys').document(request.user.username).get()
    privateKey = myKey.to_dict()['privateKey']
    decryptor = PKCS1_OAEP.new(RSA.import_key(privateKey))
    try:
        newMsg = decryptor.decrypt(msg)
        newMsg = newMsg.decode('utf-8')
        if ifAttachment is True:
            messages.info(request,mark_safe(newMsg),extra_tags=id)
        else:
            messages.info(request,mark_safe(newMsg),extra_tags="noData")
    except:
        messages.info(request,msg,extra_tags="noData")
    return redirect('home')

def seeOutbox(request,id):
    firebaseDatabaseConnection()
    myDB= firestore.client()
    myData=myDB.collection('usersDB').document(request.user.username).collection('outbox').where("id","==",id).get()
    myObject= list(myData)[0].to_dict()
    msg=myObject['message']
    attachmentURL = ""
    try:
        attachmentURL = myObject['attachmentArray'][0]
    except:
        pass
    ifAttachment = False
    try:
        ifAttachment = myObject['attachment']
    except:
        pass
    myKey=myDB.collection('privateKeys').document(request.user.username).get()
    privateKey = myKey.to_dict()['privateKey']
    decryptor = PKCS1_OAEP.new(RSA.import_key(privateKey))
    try:
        newMsg = decryptor.decrypt(msg)
        newMsg = newMsg.decode('utf-8')
        if ifAttachment is True:
            messages.warning(request,newMsg,extra_tags=id)
        else:
            messages.warning(request,newMsg,extra_tags="noData")
    except:
        messages.warning(request,msg,extra_tags="noData")
    return redirect('home')

def logoutUser(request):
    logout(request)
    return redirect('home')

def attachmentContent_Inbox(request,id):
    content = "hidden"
    boxType = "inbox"
    extensionList = []
    contentArray = []
    temporaryList = {}
    if request.method == "POST":
        passCode = request.POST['secretcode']
        databaseObject = userDatabase.objects.get(username = request.user.username)
        dateOfBirth = databaseObject.dateOfBirth
        phoneNumber = databaseObject.phoneNumber
        truePasscode = str(dateOfBirth)[:-6]+phoneNumber[6:]
        if passCode == truePasscode:
            content = "show"
            boxType = "outbox"
            id = id[:-5]
            firebaseDatabaseConnection()
            myDB= firestore.client()
            myData=myDB.collection('usersDB').document(request.user.username).collection('inbox').where("id","==",id).get()
            myObject= list(myData)[0].to_dict()
            attachments = myObject['attachmentArray']
            extension = myObject['attachmentType']
            try:
                extensionList = myObject['extensionList']
            except:
                extensionList.append(extension)
            for i in range(len(extensionList)):
                temporaryList['extensionType'] = extensionList[i]
                temporaryList['attachmentURL'] = attachments[i]
                contentArray.append(temporaryList.copy())
                temporaryList.clear()
        else:
            return HttpResponse("Password Wrong")
    context = {
        'boxType' : boxType ,
        'content' : content,
        'contentArray':contentArray,
    }
    return render(request,'user/seeAttachment.html',context)
#################################################################
#Testing
def attachmentContent_Outbox(request,id):
    content = "show"
    extensionList = []
    contentArray = []
    temporaryList = {}
    id = id[:-8]
    print(len(id),request.user.username)
    firebaseDatabaseConnection()
    myDB= firestore.client()
    myData=myDB.collection('usersDB').document(request.user.username).collection('outbox').where("id","==",id).get()
    myObject= list(myData)[0].to_dict()
    attachments = myObject['attachmentArray']
    extension = myObject['attachmentType']
    try:
        extensionList = myObject['extensionList']
    except:
        extensionList.append(extension)
    for i in range(len(extensionList)):
        temporaryList['extensionType'] = extensionList[i]
        temporaryList['attachmentURL'] = attachments[i]
        contentArray.append(temporaryList.copy())
        temporaryList.clear()
    context = {
        'boxType' : "outbox",
        'content' : content,
        'contentArray':contentArray,
    }
    return render(request,'user/seeAttachment.html',context)
#################################################################
