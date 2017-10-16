# simplest chat server

import socket
import select
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server_socket.setblocking(0)

        #self.clients = {}
        self.sockets = []

        # bind socket to server using hostname and port
        try:
            self.server_socket.bind((self.host, self.port))
        except:
            print('Failed to bind socket to server'.format(socket.error))
            sys.exit()

        # listen up to n_connections
        self.server_socket.listen(n_connections)

        # add open socket to socket list
        self.sockets.append(self.server_socket)

        print(self.server_socket)
        print("Chat server started on port " + str(PORT))


    def run(self):

        print('Waiting for connections on port'.format(self.port))


        while True:

            # get list of sockets which are readable, writable or have an exceptional condition
            # all sockets in readable have data buffered to be read out
            # all sockets in writable have free space in the buffer to be written to
            readable_sockets, writable_sockets, exceptional_sockets = select.select(self.sockets, [], [], 0)

            for socket in readable_sockets:

                if socket == self.server_socket:
                    # new connection
                    conn, addr = self.server_socket.accept()
                    self.sockets.append(conn)
                    print("new client connected: {0}, {1}".format(conn, addr))

                    self.publish_to_all(conn, "[%s:%s] entered our chatting room\n" % addr)


                else: # message from client

                    data = socket.recv(RECV_BUFFER)
                    print("Received ", repr(data))

                    if data:
                        self.publish_to_all(socket, "\r" + '[' + str(socket.getpeername()) + '] ' + data.decode())
                    else:
                        # remove the socket that's broken
                        if socket in self.sockets:
                            self.sockets.remove(socket)

                        self.publish_to_all(socket, "Client (%s, %s) is offline\n" % addr)

        conn.close()


    def publish_to_all(self, socket, message):

        for isocket in self.sockets:

            if isocket != self.server_socket and isocket != socket:
                try:
                    isocket.send(message)
                except:
                    isocket.close()
                    if isocket in self.sockets:
                        self.sockets.remove(isocket)


    def stop(self):
        pass


if __name__ == '__main__':

    chat_server = ChatServer(PORT, HOST)
    chat_server.run()
