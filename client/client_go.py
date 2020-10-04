#!/usr/bin/env python3
import socket
import sys
import os

HOST = ''  # The server's hostname or IP address
PORT = 7006  # The port used by the server
DATA_PORT = PORT + 1
HEADERSIZE = 10
BUFFER = 64


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


def get(host, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, DATA_PORT))

            data = bytearray()
            while True:
                bdata = s.recv(BUFFER)
                data += bdata
                if not bdata: break

            with open(filename, "w") as f:
                sdata = data.decode("utf-8")
                f.write(sdata)
                f.close()
            sys.exit(0)
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def send(control, host, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, DATA_PORT))
            send_msg(control, "SEND_READY", '')
            with s:
                if os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        send_file(s, f)
                else:
                    print(f"{filename} doesn't exist on client")
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def init_connection(host, action, filename):
    host = host or HOST
    print(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, PORT))
            while True:
                full_msg = ''
                new_msg = True
                while True:
                    msg = s.recv(16)
                    if new_msg:
                        print(f"new message length: {msg[:HEADERSIZE]}")
                        msglen = int(msg[:HEADERSIZE])
                        new_msg = False

                    full_msg += msg.decode("utf-8")
                    if len(full_msg) - HEADERSIZE == msglen:
                        print("full msg recvd")
                        print(full_msg[HEADERSIZE:])
                        if full_msg[HEADERSIZE:] == "GET_READY":
                            get(host, filename)
                            print("amistuck")
                        elif full_msg[HEADERSIZE:] == "SEND_READY":
                            send(s, host, filename)
                        new_msg = True
                        full_msg = ''

                    if action == "GET":
                        s.send(
                            bytes(f"{len(action):<{HEADERSIZE}}" + action + filename, "utf-8"))
                    elif action == "SEND":
                        s.send(
                            bytes(f"{len(action):<{HEADERSIZE}}" + action + filename, "utf-8"))
                    elif action == "CLOSE":
                        s.send(
                            bytes(f"{len(action):<{HEADERSIZE}}" + action, "utf-8"))

        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <host> <action> <filename>")
        sys.exit(1)
    host, action, filename = sys.argv[1], sys.argv[2], sys.argv[3]

    init_connection(host, action, filename)


if __name__ == '__main__':
    main()
