# simplest chat server

import socket
import sys

HOST = "localhost"
PORT = 8000
RECV_BUFFER = 4096

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen(1)
# print("Chat server started on port " + str(PORT))
#
#
# conn, addr = s.accept()
# print("connected: {0}, {1}".format(conn, addr))
#
# while True:
#     data = conn.recv(1024)
#     print("Received ", repr(data))
#
#     reply = input("Reply: ")
#     conn.sendall(reply.encode())
#
# conn.close()

class ChatServer():

    def __init__(self, port, host='localhost', n_connections=10):

        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}

        try:
            self.server.bind((self.host, self.port))
        except:
            print('Failed to bind socket to server'.format(socket.error))
            sys.exit()

        self.server.listen(n_connections)
        print("Chat server started on port " + str(PORT))

    def run(self):

        print('Waiting for connections on port'.format(self.port))

        while True:
            conn, addr = self.server.accept()
            print("new client connected: {0}, {1}".format(conn, addr))

            data = conn.recv(RECV_BUFFER)
            print("Received ", repr(data))

        conn.close()

    def stop(self):
        pass


if __name__ == '__main__':

    chat_server = ChatServer(PORT, HOST)
    chat_server.run()
