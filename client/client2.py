#!/usr/bin/env python3
import socket
import sys
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 1 #currently set to 1KB
host = '192.168.1.80'  #The server's hostname or IP address
port = 7005  #The port used by the server

def sender(host, filename):
    
    filesize = os.path.getsize(filename)#size of file
    try:
        s = socket.socket()
        print(f"Sending on {host}:{port}")
        s.connect((host, port))
        s.send(f"{filename}{SEPARATOR}{filesize}".encode()) # send the filename and filesize
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:       
            for _ in progress:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break #this happens when the size = original
                s.sendall(bytes_read)
                progress.update(len(bytes_read)) #progress bar for jokes

    except KeyboardInterrupt:
        print("Unexpected keyboard Interruption. Closing connections!")
        s.close()
        sys.exit(0)
    s.close() 
    print("Sent File:"+filename)

def reciever(host, filename):
    #host = host or HOST
    print(host)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            with open('received_file', 'wb') as f:
                while True:
                    print("receiving data...")
                    data = s.recv(BUFFER_SIZE)
                    print(f"data=${data}")
                    if not data:
                        f.close()
                        break
                    f.write(data)
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            print("Received File"+filename)
    except KeyboardInterrupt:
        print("Unexpected keyboard Interruption. Closing connections!")
        s.close()
        sys.exit(0)

def init_connection(host, filename, action):
    # using_file = ''
    # if action == "SEND" or action == "send":
    #         using_file = 'SEND.txt'            
    #     elif action == "GET" or action == "get":
    #         using_file = 'GET.txt'    
    #     else:
    #         print("Use: SEND or GET as an <action>")
    #         sys.exit(0)

    try:
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     #s.send(b'BEGIN')
        #     while True: #check this later
        #         files_sent = [using_file, filename]
        #         for file in files_sent:
        #             with open(file, 'rb') as Ftag:
        #                 s.sendall(Ftag.read())
        #             print('File sent!')    


        # initial_msg = action#is GET.txt or SEND.txt
        # #this confirms what it do
        # #then sends second connection
        if action == "SEND" or action == "send":
            sender(host, filename)
            
        if action == "GET" or action == "get":
            reciever(host, filename)
        # no longer in use. see above    
        # else:
        #     print("Use: SEND or GET as an <action>")
        #     sys.exit(0)

    except KeyboardInterrupt:
        print("Unexpected keyboard Interruption. Closing connections!")
        s.close()
        sys.exit(0)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <host> <action> <filename>")
        sys.exit(1)
    host, action, filename = sys.argv[1], sys.argv[2], sys.argv[3]

    init_connection(host, filename, action)


if __name__ == '__main__':
    print("Client is Clienting.")
    main()
