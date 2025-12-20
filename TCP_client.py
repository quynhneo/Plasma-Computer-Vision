# import socket
# import time


# CRIO_IP = "192.164.1.2"
# #CRIO_IP = "127.0.0.1"
# PORT = 5010

# with socket.create_connection((CRIO_IP, PORT)) as s:
#     val = False
#     while True:
#         val = not val
#         print("sending", 1 if val else 0)
#         s.sendall(b"\x01" if val else b"\x00")
#         time.sleep(1)

import socket
import struct
import time

CRIO_IP = "192.164.1.2"   # change if needed
PORT = 5010

print("Connecting to", CRIO_IP, PORT)

with socket.create_connection((CRIO_IP, PORT), timeout=5) as s:
    print("Connected")

    values = [0.25, 0.25]
    idx = 0

    while True:
        v = values[idx]
        idx = 1 - idx   # toggle index: 0 <-> 1

        # Pack as LITTLE-ENDIAN float32 (4 bytes)
        payload = struct.pack(">f", v)

        print(f"Sending {v} -> bytes {payload.hex()}")
        s.sendall(payload)

        time.sleep(1.0)
