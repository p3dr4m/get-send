#!/usr/bin/env python3

import socket
import sys
import os
from pathlib import Path

HOST = ""
PORT = 7005
DATA_PORT = PORT + 1
HEADERSIZE = 10
BUFFER = 64


def recv_msg(s):
    """
    Helper function to receive the message
    Message format:
    {HEADER_LENGTH}{ACTION}{PAYLOAD}
    """
    data = b""
    while True:
        part = s.recv(BUFFER)
        data += part
        if len(part) < BUFFER:
            break
    try:
        msglen = int(data[:HEADERSIZE].decode())
    except ValueError:
        msglen = 0

    data_len = len(data)
    action_len = data_len - (HEADERSIZE + msglen)
    payload_start = HEADERSIZE + action_len
    action = data[HEADERSIZE : HEADERSIZE + action_len].decode()
    payload = data[payload_start:].decode()
    return payload, action, msglen


def send_msg(s, msg, action):
    """
    Message format:
    {HEADER_LENGTH}{ACTION}{PAYLOAD}
    creates the message and sends it
    """
    msg = f"{len(msg):<{HEADERSIZE}}" + action + msg
    s.sendall(bytes(msg, "utf-8"))


def send_file(s, f):
    """
    Helper that stitches the file back together
    """
    part = f.read(BUFFER)
    while part:
        s.send(part)
        print(f"Sent ${repr(part)}")
        part = f.read(BUFFER)


def get(host, filename):
    """
    Connects to the data channel and asks the server for a file
    stiches the file and writes it to disk
    then close
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, DATA_PORT))

            data = bytearray()
            while True:
                bdata = s.recv(BUFFER)
                data += bdata
                if not bdata:
                    break

            with open(Path(filename).name, "wb") as f:
                f.write(data)
                f.close()
            s.close()
            sys.exit(0)
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def send(control, host, filename):
    """
    Connects to the data_channel.
    check if file exists
    then opens file as bytes and sends them to the server
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, DATA_PORT))
            with s:
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        send_file(s, f)
                else:
                    print(f"{filename} doesn't exist on client")
            sys.exit(0)
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def control_connect(host, action, filename):
    """
    The client side control channel connection.
    Sends and receives messages from server to act accordingly
    Should refactor but w.e
    """
    host = host or HOST
    print(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, PORT))
            while True:
                payload, action_recv, msglen = recv_msg(s)

                if action_recv == "GET_READY":
                    get(host, filename)
                elif action_recv == "SEND_READY":
                    send(s, host, filename)

                if action == "GET":
                    send_msg(s, filename, action)
                elif action == "SEND":
                    send_msg(s, filename, action)
                elif action == "CLOSE":
                    send_msg(s, "", action)

        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def main():
    """
    checks if the amount of arguments are correct and if not spits out a simple usage print
    parse the args and send them to the client control_channel function
    """
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <host> <action> <filename>")
        sys.exit(1)
    host, action, filename = sys.argv[1], sys.argv[2], sys.argv[3]

    control_connect(host, action, filename)


if __name__ == "__main__":
    main()
