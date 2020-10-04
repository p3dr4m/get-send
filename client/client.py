#!/usr/bin/env python3
import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7005  # The port used by the server


def init_connection(host, filename):
    host = host or HOST
    print(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, PORT))
        with open('received_file', 'wb') as f:
            while True:
                print("receiving data...")
                data = s.recv(1024)
                print(f"data=${data}")
                if not data:
                    f.close()
                    break
                f.write(data)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print("Received File")


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <host> <action> <filename>")
        sys.exit(1)
    host, action, filename = sys.argv[1], sys.argv[2], sys.argv[3]

    init_connection(host, filename)


if __name__ == '__main__':
    main()
