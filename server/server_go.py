#!/usr/bin/env python3

import socket
import sys
import time
import os

HOST = '0.0.0.0'
PORT = 7005
DATA_PORT = PORT + 1
HEADERSIZE = 10
BUFFER = 64

def data_channel(action, control, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, DATA_PORT))
            s.listen(2)
            print(f"Data Channel: Listening on {HOST}:{DATA_PORT}")
            while True:
                if action == "GET":
                    send_msg(control, "GET_READY", '')
                    client_socket, address = s.accept()
                    with client_socket:
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                send_file(client_socket, f)
                        else:
                            send_msg(client_socket, f"{filename} doesn't exist on server", "CLOSE")
                    print("Closing Data Channel")
                    break

                elif action == "SEND":
                    send_msg(control, "SEND_READY", '')
                    client_socket, address = s.accept()
                    data = client_socket.recv(BUFFER)
                    payload, action, hdr_len = recv_msg(client_socket)
                    with open(filename, "wb") as f:
                        while True:
                            if action:
                                continue
                            data = client_socket.recv(BUFFER)
                            if not data:
                                f.close()
                                break
                            f.write(data)
                    break
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def recv_msg(s):
    data = b''
    while True:
        part = s.recv(BUFFER)
        data += part
        if len(part) < BUFFER:
            break
    try:
        hdr_len = int(data[:HEADERSIZE].decode())
    except ValueError:
        hdr_len = 0
    action = data[HEADERSIZE:HEADERSIZE + hdr_len].decode()
    payload = data[HEADERSIZE + hdr_len:].decode()
    return payload, action, hdr_len

def send_msg(s, msg, action):
    msg = f"{len(msg):<{HEADERSIZE}}" + action + msg
    s.sendall(bytes(msg, "utf-8"))

def send_file(s, f):
    part = f.read(BUFFER)
    while part:
        s.send(part)
        print(f"Sent ${repr(part)}")
        part = f.read(BUFFER)

def control_channel():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(2)
            print(f"Listening on {HOST}:{PORT}")

            while True:
                client_socket, address = s.accept()
                print(f"Connected from ${address}")
                send_msg(client_socket, "Hello from Server", '')

                payload, action, hdr_len = recv_msg(client_socket)
                print(action)
                if action == "GET" or action == "SEND":
                    data_channel(action, client_socket, payload)
                
                
                if action == "CLOSE":
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    sys.exit(0)


                # client_socket.close()

        except KeyboardInterrupt:
            print("KeyboardInterrupt: Closing connections")
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            sys.exit(1)

if __name__ == '__main__':
    control_channel()
