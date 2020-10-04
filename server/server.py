#!/usr/bin/env python3

import socket
import sys

HOST = ''
PORT = 7005


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen(2)
            print(f"Listening on {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                print(f"Connected by ${addr}")
                # print("Server received", repr(data))
                with conn:
                    with open('serverfile.txt', 'rb') as f:
                        packet = f.read(1024)
                        while packet:
                            conn.send(packet)
                            print(f"Sent ${repr(packet)}")
                            packet = f.read(1024)
                        print("Done Sending")
        except KeyboardInterrupt:
            print("Unexpected Interrupt. Closing connections")
            s.close()
            sys.exit(0)



if __name__ == '__main__':
    main()
