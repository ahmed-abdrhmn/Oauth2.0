import os
from socket import *
from urllib import request, parse, error
import webbrowser
import json

port = 8333
client_id = '964584154021-1oamn21a6kqks8v0s6svi9caacsbo3g9.apps.googleusercontent.com'
client_secret = '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'
redirect_uri = f'http://127.0.0.1:{port}'
scope = 'https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.readonly'
access_token = None
refresh_token = None

def getRefreshAndAccessTokens():
    global port, client_id, client_secret, redirect_uri, scope, access_token, refresh_token
    #----------------------------Create Socket for Request-----------------------------
    ls = socket(AF_INET,SOCK_STREAM)

    ls.bind(('127.0.0.1',port))

    ls.listen()
    #----------------------------Open Browser for Request------------------------------

    query = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri':redirect_uri,
        'scope':scope
    }

    webbrowser.open(f'https://accounts.google.com/o/oauth2/v2/auth?{parse.urlencode(query)}',1)
    #----------------------------------Get Response(Auth code)-------------------------

    cs,_ = ls.accept()
    print('Connect Recieved')

    code = ''

    cs.recv(11) #ignore first 11 characters

    while True:
        char = cs.recv(1).decode('ascii')
        if(char == '&'):
            break
        else:
            code += char

    #-----Empty Socket-------        
    cs.setblocking(False)        
    try:
        while True:
            cs.recv(4096)
    except BlockingIOError:
        pass

    #--------------------------------Send Response to Browser--------------------------        
    file = open('resp.txt','rb')
    response = file.read()
    cs.sendall(response)
    file.close()
    cs.close()
    ls.close()

    #--------------------------Request Access and Refresh Tokens-----------------------
    query = {
        'client_id':client_id,
        'client_secret':client_secret,
        'code':code,
        'grant_type':'authorization_code',
        'redirect_uri':redirect_uri
    }


    req = request.Request(f'https://oauth2.googleapis.com/token?{parse.urlencode(query)}',method='POST')

    auth = request.urlopen(req)

    #--------------------------Store the Access and refresh tokens for later use
    response = json.loads(auth.read().decode('ascii'))

    output = open('res.txt','w')
    access_token = response['access_token']
    refresh_token = response['refresh_token']
    output.write(access_token)
    output.write('\n')
    output.write(refresh_token)
    output.close()
    
def getAccessToken():
    global client_id, client_secret, refresh_token, access_token
    query = {
        'client_id':client_id,
        'client_secret':client_secret,
        'grant_type':'refresh_token',
        'refresh_token':refresh_token
    }
    
    req = request.Request(f'https://oauth2.googleapis.com/token?{parse.urlencode(query)}', method='POST')
    
    auth = request.urlopen(req)
    
    access_token = json.loads(auth.read().decode('ascii'))['access_token']
    output = open('res.txt','w')
    output.write(access_token)
    output.write('\n')
    output.write(refresh_token)
    output.close()
    
def Attempt():
    query = {
        'part':'snippet',
        'myRating':'like',
        'maxResults':'12'
    }

    headers = {
        'Authorization' : f'Bearer {access_token}'
    }

    req = request.Request(f'https://www.googleapis.com/youtube/v3/videos?{parse.urlencode(query)}', method='GET', headers=headers)
    return request.urlopen(req)

#---------------------------MAIN ROUTINE--------------------------------
tokens = open('res.txt','r')
access_token = tokens.readline()[:-1]
refresh_token = tokens.readline()
tokens.close()

videos = None
try:
    videos = Attempt()
except error.HTTPError as e:
    try:
        print(e,end=': ')
        print('invalid Access Token')
        getAccessToken()
    except Exception as e:
        try:
            print(e,end=': ')
            print('invalid Refresh Token')
            getRefreshAndAccessTokens()
        except Exception as e:
            print(e,end=': ')
            print('something\'s REALLY wrong here')
    
    try:
        videos = Attempt()
    except Exception as e:
        print(e,end=': ')
        print('I give up')
        os.system('pause')
        exit()

#Printing the list of liked videos            
resultString = videos.read().decode('utf-8')    
list = json.loads(resultString)
for i in list['items']:
    print(i['snippet']['title'])

os.system('pause')
