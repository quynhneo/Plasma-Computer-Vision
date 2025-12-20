import socket
import time


CRIO_IP = "192.164.1.2"
#CRIO_IP = "127.0.0.1"
PORT = 5010

with socket.create_connection((CRIO_IP, PORT)) as s:
    val = False
    while True:
        val = not val
        print("sending", 1 if val else 0)
        s.sendall(b"\x01" if val else b"\x00")
        time.sleep(1)

