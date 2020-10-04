#!/usr/bin/env python3
import socket
import sys
import tqdm
import os

host = '192.168.1.80'  #This device's hostname or IP address
port = 7005  #The port used by this device
BUFFER_SIZE = 1024 * 1 #currently set to 1KB
SEPARATOR = "<SEPARATOR>"

def sending():
    try:
        while Not_sent == True:
            client, addr = s.accept()
            print(f"Connected by ${addr}")
            #print("Server received", repr(data))

            # request_specific = client.recv(buffer_size).decode()
            # filename, filesize = received.split(SEPARATOR)
            # filename = os.path.basename(filename)
            # filesize = int(filesize) #update to int
            #HERE

            with client:
                with open('serverfile.txt', 'rb') as f:
                    packet = f.read(BUFFER_SIZE)
                    print("chumbus:",packet)
                    while packet:
                        client.send(packet)
                        print(f"Sent ${repr(packet)}")
                        packet = f.read(BUFFER_SIZE)
                    print("Done Sending")
                    Not_sent = False
    except KeyboardInterrupt:
        print("Unexpected keyboard Interruption. Closing connections!")
        s.close()
        client.close()
        sys.exit(0)

def receiving():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            client, addr = s.accept()
            received = client.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)
            filename = os.path.basename(filename)
            filesize = int(filesize)
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                for _ in progress:
                    bytes_read = client.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
            
    except KeyboardInterrupt:
        print("Unexpected keyboard Interruption. Closing connections!")
        s.close()
        client.close()
        sys.exit(0)
    finally:
        s.close()
        client.close()
        sys.exit(0)

def main():
    Not_sent = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # s.bind((host, port))
            # s.listen(100) #number of unaccepted connects before one is connected
            # print(f"Listening on {host}:{port}")
            # while Not_sent == True:
            #     client, addr = s.accept()
            #     print(f"Connected by ${addr}")
            #     #print("Server received", repr(data))
            #     request_specific = client.recv(BUFFER_SIZE).decode()
            #     filename, filesize = received.split(SEPARATOR)
            #     filename = os.path.basename(filename)
            #     filesize = int(filesize) #update to int
            #     #HERE

            #     with client:
            #         with open('serverfile.txt', 'rb') as f:
            #             packet = f.read(BUFFER_SIZE)
            #             while packet:
            #                 client.send(packet)
            #                 print(f"Sent ${repr(packet)}")
            #                 packet = f.read(BUFFER_SIZE)
            #             print("Done Sending")
            #             Not_sent = False
            s.bind((host,port))
            s.listen(100)
            while True:

        except KeyboardInterrupt:
            print("Unexpected keyboard Interruption. Closing connections!")
            s.close()
            client.close()
            sys.exit(0)
        finally:
            s.close()
            client.close()
            sys.exit(0)


if __name__ == '__main__':
    print("Server is Servering.")
    main()