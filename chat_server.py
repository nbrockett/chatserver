# simplest chat server

import socket
import select
import sys
import argparse


#HOST = "localhost"
#PORT = 8000
RECV_BUFFER = 4096
FLAGS = None

class ChatRoom():

    def __init__(self, room_name):

        self.room_name = room_name




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
        print("Chat server started on port " + str(self.port))


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
                    conn_socket, addr = self.server_socket.accept()
                    self.sockets.append(conn_socket)
                    print("new client from: {0}".format(addr))

                    self.publish_to_all(conn_socket, "[%s:%s] entered our chatting room\n" % addr)
                    print("[%s:%s] entered our chatting room\n" % addr)

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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='host ip of server.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='port of server.'
    )

    FLAGS, unparsed = parser.parse_known_args()

    chat_server = ChatServer(FLAGS.port, FLAGS.host)
    chat_server.run()
