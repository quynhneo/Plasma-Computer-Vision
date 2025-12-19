import socket
import time

CRIO_IP = "192.164.1.2"
PORT = 5005

with socket.create_connection((CRIO_IP, PORT)) as s:
    val = False
    while True:
        val = not val
        s.sendall(b"\x01" if val else b"\x00")
        time.sleep(0.5)
