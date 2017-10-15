# simplest chat server

import socket

HOST = "localhost"
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("Chat server started on port " + str(PORT))


conn, addr = s.accept()
print("connected: {0}, {1}".format(conn, addr))

while True:
    data = conn.recv(1024)
    print("Received ", repr(data))

    reply = input("Reply: ")
    conn.sendall(reply.encode())

conn.close()
