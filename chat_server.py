# simplest chat server

import socket
import select
import sys
import argparse
import threading
from itertools import count
import subprocess
import time

#HOST = "localhost"
#PORT = 8000
RECV_BUFFER = 4096
MAX_CONNECTIONS = 10
FLAGS = None




class Connection:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.ip = address[0]
        self.port = address[1]

class ChatRoom:

    def __init__(self, room_name, room_ID):

        self.room_name = room_name
        self.room_ID = room_ID

        # list of client names
        self.clients = {}
        self.client_sockets = []


    def add_client(self, join_ID, client_name, sock):

        if join_ID not in self.clients:
            self.clients[join_ID] = (client_name, sock)
        else:
            print("client ID {0} already joined".format(join_ID))

    def remove_client(self, join_ID, client_name):

        if join_ID in self.clients:
            if self.clients[join_ID][0] == client_name:
                del self.clients[join_ID]

    def get_client_sockets(self):
        """" returns list of sockets for current chat room clients """

        return [val[1] for val in list(self.client_sockets.values())]

    def publish_to_clients(self, message):
        """ push a message to currently connected clients of the chat room"""

        # Return:
        # CHAT: [ROOM_REF]
        # CLIENT_NAME: [string identifying client user]
        # MESSAGE: [string terminated with '\n\n']

        # socket_list = self.get_client_sockets()

        for client_name, isocket in self.clients.values():
            try:
                msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {2}\n\n".format(self.room_ID, client_name, message)
                isocket.send(msg)
            except:
                # if isocket in self.sockets:
                #     self.sockets.remove(isocket)
                isocket.close()

class ChatServer(threading.Thread):

    def __init__(self, port, host='localhost', n_connections=MAX_CONNECTIONS):

        threading.Thread.__init__(self)

        # Server parameters
        self.port = port
        self.host = host
        self.server_socket = None
        self.running = True

        #self.clients = {}
        self.sockets = []
        self.chat_rooms = {}

        # counter for connections IDs
        self.counter = count()
        self.chat_room_ID = 0
        self.join_ID = 0

        self.bind_socket(n_connections)

        # add open socket to socket list
        self.sockets.append(self.server_socket)

        self.socket_list = {}

        self.connections = []

        print(self.server_socket)
        print("Chat server started on port " + str(self.port))


    def bind_socket(self, n_connections):

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(n_connections)
            # self.connections.append(self.server_socket)
        except:
            print('Failed to bind socket to server'.format(socket.error))
            sys.exit()

    def run(self):

        print('Waiting for connections on port'.format(self.port))
        while True:

            # get list of sockets which are readable, writable or have an exceptional condition
            # all sockets in readable have data buffered to be read out
            # all sockets in writable have free space in the buffer to be written to
            # readable_sockets, writable_sockets, exceptional_sockets = select.select(self.sockets, [], [], 0)

            # new connection
            try:
                conn_socket, addr = self.server_socket.accept()
            except:
                print("SOCKET ERROR!")
                return

            connection = Connection(conn_socket, addr)
            self.connections.append(connection)

            self.sockets.append(conn_socket)
            print("new client from: {0}".format(addr))
            # addr[0] = IP, addr[1] = Port
            self.socket_list[conn_socket] = (addr[0], addr[1], 'StudentId' + str(next(self.counter)))

            # for socket in readable_sockets:
            conn_socket.settimeout(60)

            threading.Thread(target=self.listen_to_socket, args=(conn_socket, addr)).start()

            # for socket in readable_sockets:
            # threading.Thread(target=self.run_thread, args=(readable_sockets,)).start()


    def listen_to_socket(self, socket, addr):

        # print('Waiting for connections on port'.format(self.port))
        # while True:
        #
        #     # get list of sockets which are readable, writable or have an exceptional condition
        #     # all sockets in readable have data buffered to be read out
        #     # all sockets in writable have free space in the buffer to be written to
        #     readable_sockets, writable_sockets, exceptional_sockets = select.select(self.sockets, [], [], 0)
        #
        #     for socket in readable_sockets:

        # for socket in readable_sockets:
        # if socket == self.server_socket:
        #     # self.add_connection()
        #
        #     # new connection
        #     try:
        #         conn_socket, addr = self.server_socket.accept()
        #     except socket.error:
        #         return
        #
        #     connection = Connection(conn_socket, addr)
        #     self.connections.append(connection)
        #
        #     self.sockets.append(conn_socket)
        #     print("new client from: {0}".format(addr))
        #     # addr[0] = IP, addr[1] = Port
        #     self.socket_list[conn_socket] = (addr[0], addr[1], 'StudentId' + str(next(self.counter)))
        #     # self.publish_to_all(conn_socket, "[%s:%s] entered our chatting room\n" % addr)
        #     # print("[%s:%s] entered our chatting room\n" % addr)
        #
        #
        # else:  # message from client
        time.sleep(0.1)
        while True:
            # subprocess.call(["sleep", "10"])
            try:
                data = socket.recv(RECV_BUFFER)
                print("Received ", repr(data.decode()))
                print("Received from ", self.socket_list[socket][0])

                if data:

                    input = data.decode()
                    print("input = ", input)

                    # handle kill
                    if input == 'KILL_SERVICE':
                        print("stopping server...")
                        self.stop()

                    # handle helo
                    elif input.startswith('HELO '):
                        print("HELO server...")
                        socket.send("{0}\nIP:{1}\nPort:{2}\nStudentID:{3}\n".format(input, str(self.socket_list[socket][0]), str(self.socket_list[socket][1]), self.socket_list[socket][2]).encode())

                    # handle commands
                    message_list = split_message(input)
                    n_actions = len(message_list)
                    first_action = message_list[0][0]

                    reply = None
                    # command: join chatroom
                    if first_action == 'JOIN_CHATROOM':
                        print('Join Chatroom request')
                        reply = self.join_chatroom(message_list, socket)
                    elif first_action == 'LEAVE_CHATROOM':
                        print('Leave Chatroom request')
                        reply = self.leave_chatroom(message_list, socket)

                    # send replt to all sockets
                    if reply:
                        self.publish_to_all(None, reply.encode())
                        # self.publish_to_all(socket, reply.encode())

                    # self.publish_to_all(socket, "\r" + '[' + str(socket.getpeername()) + '] ' + data.decode())

                else:  # data is None
                    # remove the socket that's broken
                    print("no data from socket")
                    if socket in self.sockets:
                        print("removing socket from list")
                        self.sockets.remove(socket)
                    error_msg = create_error_message(error_code=1)
                    self.publish_to_all(socket, error_msg)
                    raise Exception


                # self.publish_to_all(socket, "Client (%s, %s) is offline\n" % addr)
            except:
                socket.close()
                return

    def join_chatroom(self, message_list, socket):

        # RECEIVED MESSAGE:
        # JOIN_CHATROOM: [chatroom name]
        # CLIENT_IP: [IP Address of client if UDP | 0 if TCP]
        # PORT: [port number of client if UDP | 0 if TCP]
        # CLIENT_NAME: [string Handle to identifier client user]

        # RETURNS:
        # JOINED_CHATROOM: [chatroom name]
        # SERVER_IP: [IP address of chat room]
        # PORT: [port number of chat room]
        # ROOM_REF: [integer that uniquely identifies chat room on server]
        # JOIN_ID: [integer that uniquely identifies client joining]

        assert(len(message_list) == 4)

        assert(message_list[0][0] == 'JOIN_CHATROOM')
        chatroom_name = message_list[0][1]
        assert(message_list[1][0] == 'CLIENT_IP')
        client_ip = message_list[1][1]
        assert(message_list[2][0] == 'PORT')
        client_port = message_list[2][1]
        assert(message_list[3][0] == 'CLIENT_NAME')
        client_name = message_list[3][1]

        if chatroom_name in self.chat_rooms:
            self.join_ID += 1
            self.chat_rooms[chatroom_name].add_client(self.join_ID, client_name, socket)
        else:
            self.join_ID += 1
            self.chat_room_ID += 1
            self.chat_rooms[chatroom_name] = ChatRoom(chatroom_name, self.chat_room_ID)
            self.chat_rooms[chatroom_name].add_client(self.join_ID, client_name, socket)

        return 'JOINED_CHATROOM: {0}\nSERVER_IP: {1}\nPORT: {2}\nROOM_REF: {3}\nJOIN_ID: {4}'.format(chatroom_name, self.host, self.port, self.chat_room_ID, self.join_ID)


    def leave_chatroom(self, message_list, socket):

        # RECEIVED MESSAGE:
        # LEAVE_CHATROOM: [ROOM_REF]
        # JOIN_ID: [integer previously provided by server on join]
        # CLIENT_NAME: [string Handle to identifier client user]

        # RETURNS:
        # LEFT_CHATROOM: [ROOM_REF]
        # JOIN_ID: [integer previously provided by server on join]

        assert(len(message_list) == 3)

        assert(message_list[0][0] == 'LEAVE_CHATROOM')
        chatroom_id = message_list[0][1]
        assert(message_list[1][0] == 'JOIN_ID')
        join_id = message_list[1][1]
        assert(message_list[2][0] == 'CLIENT_NAME')
        client_name = message_list[2][1]

        left_chatroom_id = None

        # if chatroom ID doesn't exist send error message to socket
        if chatroom_id not in self.chat_rooms.values():
            error_msg = create_error_message(2, chatroom_id)
            self.send_data_to(socket, error_msg)
            return

        for room_name, chat_room in self.chat_rooms.items():
            if chat_room.room_ID == chatroom_id:
                chat_room.remove_client(join_id, client_name)
                chat_room.publish_to_clients("Client: {0} has left the chatroom".format(client_name))
                left_chatroom_id = chat_room.room_ID

        return 'LEFT_CHATROOM: {0}\nJOIN_ID: {1}'.format(left_chatroom_id, join_id)

    def send_data_to(self, socket, message):
        try:
            socket.send(message)
        except:
            # broken socket connection may be, chat client pressed ctrl+c for example
            socket.close()
            self.sockets.remove(socket)

    # def add_connection(self):
    #     # new connection
    #     try:
    #         conn_socket, addr = self.server_socket.accept()
    #     except socket.error:
    #         return
    #
    #     connection = Connection(conn_socket, addr)
    #     self.connections.append(connection)
    #
    #     self.sockets.append(conn_socket)
    #     print("new client from: {0}".format(addr))
    #     # addr[0] = IP, addr[1] = Port
    #     self.socket_list[conn_socket] = (addr[0], addr[1], 'StudentId' + str(next(self.counter)))
    #     # self.publish_to_all(conn_socket, "[%s:%s] entered our chatting room\n" % addr)
    #     # print("[%s:%s] entered our chatting room\n" % addr)

    def publish_to_all(self, socket, message):

        print("publishing message : ", message)

        for isocket in self.sockets:

            # Do not send the message to master socket and the client who has send us the message
            if isocket != self.server_socket and isocket != socket:
            # if isocket != self.server_socket:
                try:
                    isocket.send(message)
                except:
                    isocket.close()
                    if isocket in self.sockets:
                        self.sockets.remove(isocket)


    def stop(self):
        self.running = False
        self.server_socket.close()
        sys.exit(0)


def split_message(message):
    s_lines = message.split('\n')
    command_list = [s.split(': ') for s in s_lines]
    if command_list[-1] == ['']:
        del command_list[-1]
    # print([s.split(': ') for s in s_lines])
    print(command_list)

    return command_list

def create_error_message(error_code, *args):

    ERROR_MSG = "ERROR_CODE: {0}\n ERROR_DESCRIPTION: {1}\n"
    if error_code == 1:
        desc = "Error in socket connection"
        return ERROR_MSG.format(error_code, desc)
    elif error_code == 2:
        desc = "ERROR: Chatroom ID {0} doesn't exist".format(args[0])
        return ERROR_MSG.format(error_code, desc)

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
