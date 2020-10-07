#!/usr/bin/env python3
"""
--  SOURCE FILE:    client.py
--  PROGRAM:        client.py
--  FUNCTIONS:      <function headers>
--  DATE:           October 5th, 2020
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  NOTES:
--  Connects to the control channel socket, sends messages to the server, 
--  listens for messages from the server and
--  then connects to the data channel socket. File transfer happen on data
--  channel socket.
"""

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
--------------------------------------------------------------------------
--  FUNCTION:       recv_msg
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      recv_msg(s)
--  RETURNS:        string message, string action, int msglen
--  NOTES:
--  Receives a buffered message
--------------------------------------------------------------------------
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
    message_start = HEADERSIZE + action_len
    action = data[HEADERSIZE : HEADERSIZE + action_len].decode()
    message = data[message_start:].decode()
    print(message, payload, msglen)
    return message, action, msglen


def send_msg(s, msg, action):
""" 
--------------------------------------------------------------------------
--  FUNCTION:       send_msg
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      send_msg(s, msg, action)
--  RETURNS:        void
--  NOTES:
--  Formats the message protocol then sends the message
--  Message format: {MESSAGE_LENGTH}{ACTION}{MESSAGE}
--------------------------------------------------------------------------
"""
    msg = f"{len(msg):<{HEADERSIZE}}" + action + msg
    s.sendall(bytes(msg, "utf-8"))


def send_file(s, f):
""" 
--------------------------------------------------------------------------
--  FUNCTION:       send_file
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      send_file(s, f)
--  RETURNS:        void
--  NOTES:
--  Helper that buffers the file and sends them across the socket
--------------------------------------------------------------------------
"""
    part = f.read(BUFFER)
    while part:
        s.send(part)
        print(f"Sent ${repr(part)}")
        part = f.read(BUFFER)


def get(host, filename):
""" 
--------------------------------------------------------------------------
--  FUNCTION:       get
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      get(host, filename)
--  RETURNS:        void
--  NOTES:
--  Connect to the data_channel socket
--  Receive file from server and store as bytearray
--  Write bytearray as file in current directory
--  Exit client successfully
--------------------------------------------------------------------------
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


def send(host, filename):
""" 
--------------------------------------------------------------------------
--  FUNCTION:       send
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      send(host, filename)
--  RETURNS:        void
--  NOTES:
--  Connect to the data_channel socket
--  Read file from server's filesystem then calls send_file()
--  Exit client successfully
--------------------------------------------------------------------------
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
--------------------------------------------------------------------------
--  FUNCTION:       control_connect
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      control_connect(host, action, filename)
--  RETURNS:        void
--  NOTES:
--  Connects to the control channel socket on the server
--  Parses user action input and sends a message to the server
--  Listens for data_channel socket READY message to approved data socket connection
--------------------------------------------------------------------------
"""
    host = host or HOST
    print(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, PORT))

            if action == "GET":
                send_msg(s, filename, action)
            elif action == "SEND":
                send_msg(s, filename, action)
            elif action == "CLOSE":
                send_msg(s, "", action)

            while True:
                payload, action_recv, msglen = recv_msg(s)

                if action_recv == "GET_READY":
                    get(host, filename)
                elif action_recv == "SEND_READY":
                    send(host, filename)

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
