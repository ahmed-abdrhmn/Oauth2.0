import os
from socket import *
from urllib import request, parse
import webbrowser
import json

'''
response = request.urlopen('https://authorization-server.com/authorize?response_type=code&client_id=JltSzseyA-fGYkOTgDL6Bd9k&redirect_uri=https://www.oauth.com/playground/authorization-code.html&scope=photo+offline_access&state=Blablalblalbalbla') #Connect to the website

print(response)
print(response.read())
print(response.headers)

response.close()
os.system('pause')
'''
#----------------------------Create Socket for Request-----------------------------
ls = socket(AF_INET,SOCK_STREAM)

port = 8333

ls.bind(('127.0.0.1',port))

ls.listen()
#----------------------------Open Browser for Request------------------------------
client_id = '964584154021-1oamn21a6kqks8v0s6svi9caacsbo3g9.apps.googleusercontent.com'
client_secret = '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'
redirect_uri = f'http://127.0.0.1:{port}'
scope = 'https://www.googleapis.com/auth/youtube'

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
output.write(response['access_token'])
output.write('\n')
output.write(response['refresh_token'])
output.close()

os.system('pause')
    
