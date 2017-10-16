# simplest chat client

import socket

HOST = "localhost"
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    message = input("Your Message: ")
    s.send(message.encode())
    print("waiting reply")

    #reply = s.recv(1024)

    #print("Received ", repr(reply))

s.close()