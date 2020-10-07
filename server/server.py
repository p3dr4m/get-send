#!/usr/bin/env python3
"""
--  SOURCE FILE:    server.py
--  PROGRAM:        server.py
--  FUNCTIONS:      <function headers>
--  DATE:           October 5th, 2020
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  NOTES:
--  Opens the control channel socket and listens action messages
--  Upon receiving an action message, the data channel socket is opened and
--  the client is notified. Once the client has connected the file transfer takes
--  place and the socket is closed. Until the next action message.
"""

import socket
import sys
import time
import os
from pathlib import Path

HOST = "0.0.0.0"
PORT = 7005
DATA_PORT = PORT + 1
HEADERSIZE = 10
BUFFER = 64


def data_channel(action, control, filename):
""" 
--------------------------------------------------------------------------
--  FUNCTION:       data_channel
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      data_channel(action, control, filename)
--  RETURNS:        void
--  NOTES:
--  It opens a socket from the control_channel.
--  When the client sends a message with the correct action name.
--------------------------------------------------------------------------
"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, DATA_PORT))
            s.listen(2)
            print(f"Data Channel: Listening on {HOST}:{DATA_PORT}")
            if action == "GET":
                send_msg(control, "", "GET_READY")
                client_socket, address = s.accept()
                with client_socket:
                    if os.path.exists(filename):
                        with open(filename, "rb") as f:
                            send_file(client_socket, f)
                    else:
                        send_msg(
                            client_socket,
                            f"{filename} doesn't exist on server",
                            "CLOSE",
                        )
                print("Closing Data Channel")

            elif action == "SEND":
                send_msg(control, "", "SEND_READY")
                client_socket, address = s.accept()
                data = bytearray()
                with client_socket:
                    while True:
                        bdata = client_socket.recv(BUFFER)
                        data += bdata
                        if not bdata:
                            break

                    with open(Path(filename).name, "wb") as f:
                        f.write(data)
                        f.close()

                print("Closing Data Channel")
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)


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


def control_channel():
""" 
--------------------------------------------------------------------------
--  FUNCTION:       control_channel
--  DATE:           October 5th, 2020
--  REVISIONS:      N/A
--  DESIGNER:       Pedram Nazari
--  PROGRAMMER:     Pedram Nazari
--  INTERFACE:      control_channel()
--  RETURNS:        void
--  NOTES:
--  Opens the control socket and listens for action messages.
--  Executes codes based on action message.
--------------------------------------------------------------------------
"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(2)
            print(f"Listening on {HOST}:{PORT}")

            while True:
                client_socket, address = s.accept()
                print(f"Connected from ${address}")
                send_msg(client_socket, "Hello from Server", "")

                filename, action, hdr_len = recv_msg(client_socket)
                if action == "GET" or action == "SEND":
                    data_channel(action, client_socket, filename)

                if action == "CLOSE":
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    sys.exit(0)

        except KeyboardInterrupt:
            print("KeyboardInterrupt: Closing connections")
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            sys.exit(1)


if __name__ == "__main__":
    control_channel()
