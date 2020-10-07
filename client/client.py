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
import string

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
    --------------------------------------------------------------------------
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, DATA_PORT))

            if os.path.isfile(Path(filename).name):
                with open(Path(filename).name, "rb") as f:
                    send_file(s, f)
            else:
                print(f"{Path(filename).name} doesn't exist on client")

        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


def control_connect():
    """
    --------------------------------------------------------------------------
    --  FUNCTION:       control_connect
    --  DATE:           October 5th, 2020
    --  REVISIONS:      N/A
    --  DESIGNER:       Pedram Nazari
    --  PROGRAMMER:     Pedram Nazari
    --  INTERFACE:      control_connect()
    --  RETURNS:        void
    --  NOTES:
    --  Connects to the control channel socket on the server
    --  Parses user action input and sends a message to the server
    --  Listens for data_channel socket READY message to approved data socket connection
    --  Listens for FIN message to clear socket connection
    --------------------------------------------------------------------------
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <host> <action> <filename>")
        sys.exit(1)
    host = sys.argv[1]

    host = host or HOST
    print(host)
    try:
        print("Type an action")
        print("Format: <ACTION> <FILENAME>")
        print("Example: GET filename.txt")
        print("Example: SEND filename.txt")
        print("Example: CLOSE")
        command = ""
        while command != "CLOSE":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, PORT))
            command = input("Send action: ")
            filename = ""
            action, filename = (command.split(" ") + [None])[:2]

            if action == "GET":
                while True:
                    filename = Path(filename).name
                    send_msg(s, filename, action)
                    message, action_recv, msglen = recv_msg(s)
                    if action_recv == "GET_READY":
                        get(host, filename)
                        continue
                    elif action_recv == "GET_FIN":
                        print("GET FIN")
                        s = None
                        break
                    elif action_recv == "GET_FAIL":
                        print(message)
                        break
            elif action == "SEND":
                while True:
                    filename = Path(filename).name
                    send_msg(s, filename, action)
                    message, action_recv, msglen = recv_msg(s)
                    if action_recv == "SEND_READY":
                        send(host, filename)
                        continue
                    elif action_recv == "SEND_FIN":
                        print("SEND FIN")
                        s = None
                        break
            elif action == "CLOSE":
                send_msg(s, "", action)

            command = action

        sys.exit(0)
    except KeyboardInterrupt:
        s.close()
        sys.exit(1)


if __name__ == "__main__":
    control_connect()
