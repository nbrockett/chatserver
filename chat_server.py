##
##  A simple multi threaded chat server. Part of CS7NS1 course.
##
########################################################################################################################

import socket
import select
import argparse
import threading
from itertools import count
import subprocess
import time
import os
from collections import OrderedDict

RECV_BUFFER = 4096
MAX_CONNECTIONS = 10
FLAGS = None


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

        # self.publish_to_clients(str(client_name) + " has joined chatroom " + str(self.room_ID))

    def remove_client(self, join_ID, client_name):

        if join_ID in self.clients:
            if self.clients[join_ID][0] == client_name:
                del self.clients[join_ID]

    def remove_client_by_name(self, client_name):

        for join_id, val_tuple in self.clients.items():
            if val_tuple[0] == client_name:
                del self.clients[join_id]
                return

    def get_client_names(self):

        return [val[0] for val in list(self.clients.values())]

    def get_client_sockets(self):
        """" returns list of sockets for current chat room clients """

        return [val[1] for val in list(self.client_sockets.values())]

    def publish_to_clients(self, message, joined_client_name):
        """ push a message to currently connected clients of the chat room"""

        # Return:
        # CHAT: [ROOM_REF]
        # CLIENT_NAME: [string identifying client user]
        # MESSAGE: [string terminated with '\n\n']

        # socket_list = self.get_client_sockets()

        for client_name, isocket in self.clients.values():
            try:
                print("publishing to {0}, with name {1} and room ref {2}".format(client_name, joined_client_name, self.room_ID))
                msg = "CHAT: {0}\nCLIENT_NAME: {1}\nMESSAGE: {2}\n\n".format(self.room_ID, joined_client_name, message)
                isocket.send(msg.encode())
            except Exception as e:
                print("Unknwon Exception in chatroom class  ", e)
            #     # if isocket in self.sockets:
            #     #     self.sockets.remove(isocket)
            #     print("CLOSING SOCKET")
            #     isocket.close()

class ChatServer(threading.Thread):
    """
    Multi-Threaded Chat Server
    """

    def __init__(self, port=8000, host='localhost'):

        threading.Thread.__init__(self)

        self.host = host
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))

        # {socket = (Ip, port, StudentID)}
        self.socket_list = {}

        # counter for connections IDs
        self.student_ID_counter = count()
        self.chat_room_ID = 0
        self.join_ID = 0

        # {chatroom name : <ChatRoom Class>}
        self.chat_rooms = OrderedDict()

        print("Chat server started on port " + str(port))

    def run(self):
        """ run server and listen to new connections. If found create client sockets"""

        self.server.listen(MAX_CONNECTIONS)
        inputs = [self.server]
        self.client_threads = {}

        print("running chat server")

        while True:
            try:
                inready, outready, excready = select.select(inputs, [], [])
                for s in inready:
                    if s == self.server:
                        # setup new client connection
                        conn_socket, address = self.server.accept()

                        print("Connection == Server? ", conn_socket == s)

                        print("new client from: {0}".format(address))

                        client_thread = threading.Thread(target=self.listen_to_socket, args=(conn_socket, address))
                        client_thread.setDaemon(True)
                        client_thread.start()

                        self.client_threads[conn_socket] = client_thread
                        self.socket_list[conn_socket] = (address[0], address[1], 'StudentId' + str(next(self.student_ID_counter)))
            except KeyboardInterrupt:
                print("KeyboardInterrupt, shutting down server")
                os._exit(0)
            except Exception as e:
                print("Exception {0}, shutting down server".format(e))
                os._exit(0)

        self.stop()

    def listen_to_socket(self, socket, addr):
        """ threaded function for socket listening """

        time.sleep(0.1)
        running_thread = True
        while running_thread:
            # try:
                print("Socket = ", socket)
                data = socket.recv(RECV_BUFFER)
                if data:
                    # decode data stream
                    data = data.decode()

                    running_thread = self.message_parser(data, socket)
                    # if running_thread == False:
                    #     self.client_threads[socket].exit()

                else:
                    print("Error: No data from {0}".format(addr))
            # except Exception as e:
            #     print("Unknown Exception {0} occurred".format(e))


    def message_parser(self, inputdata, socket):

        print("---- Data Received -----")
        print(inputdata)
        print("------------------------")

        # handle kill
        if inputdata.startswith('KILL_SERVICE'):
            print("Stopping server...")
            self.stop()
            return True

        # handle helo
        elif inputdata.startswith('HELO '):
            # socket.send("HELLO BACK!!!! HIHIHIHII".encode())
            message = "{0}\nIP:{1}\nPort:{2}\nStudentID:{3}\n".format(inputdata, str(self.socket_list[socket][0]), str(self.socket_list[socket][1]), self.socket_list[socket][2])
            print("Reply: ", message)
            socket.send(message.encode())
            return True

        # handle commands
        message_list = split_message(inputdata)
        first_action = message_list[0][0]

        reply = None
        # command: join chatroom
        if first_action == 'JOIN_CHATROOM':
            print('Join Chatroom request')
            self.handle_join(message_list, socket)
            return True
        elif first_action == 'LEAVE_CHATROOM':
            print('Leave Chatroom request')
            self.handle_leave(message_list, socket)
            return True
        elif first_action == 'CHAT':
            print('Chat request')
            self.handle_chat(message_list, socket)
            return True
        elif first_action == 'DISCONNECT':
            print('Disconnect request')
            do_disconnect = self.handle_disconnect(message_list, socket)
            return do_disconnect

        print("MESSAGE COULD NOT BE PARSED")
        return False

    def handle_disconnect(self, message_list, socket):

        # RECEIVED
        # DISCONNECT: [IP address of client if UDP | 0 if TCP]
        # PORT: [port number of client it UDP | 0 id TCP]
        # CLIENT_NAME: [string handle to identify client user]

        print("Message List = ", message_list)
        assert (len(message_list) == 3)

        assert (message_list[0][0] == 'DISCONNECT')
        client_ip = message_list[0][1]
        assert (message_list[1][0] == 'PORT')
        port = message_list[1][1]
        assert (message_list[2][0] == 'CLIENT_NAME')
        client_name = message_list[2][1]

        # (client_ip, port, StudentID) = self.socket_list[socket]

        # if client_ip == client_ip_ and port == port_:
        del self.socket_list[socket]

        for chat_room in self.chat_rooms.values():
            iter_dic = list(chat_room.clients.values())
            for cname, sock in iter_dic:
                if client_name == cname and socket == sock:
                    chat_room.publish_to_clients("{0} has left this chatroom.".format(client_name), client_name)
                    chat_room.remove_client_by_name(client_name)

        # return False to stop thread
        return False


    def handle_chat(self, message_list, socket):

        # RECEIVED MESSAGE
        # CHAT: [ROOM_REF]
        # JOIN_ID: [integer identifying client to server]
        # CLIENT_NAME: [string identifying client user]
        # MESSAGE: [string terminated
        # with '\n\n']

        # SEND TO CHATROOM
        # CHAT: [ROOM_REF]
        # CLIENT_NAME: [string identifying client user]
        # MESSAGE: [string terminated
        # with '\n\n']

        print("Message List = ", message_list)
        assert (len(message_list) == 4)

        assert (message_list[0][0] == 'CHAT')
        room_id = message_list[0][1]
        assert (message_list[1][0] == 'JOIN_ID')
        join_id = message_list[1][1]
        assert (message_list[2][0] == 'CLIENT_NAME')
        client_name = message_list[2][1]
        assert (message_list[3][0] == 'MESSAGE')
        message = message_list[3][1]

        room_id = int(room_id)
        join_id = int(join_id)

        for chatroom in self.chat_rooms.values():
            if chatroom.room_ID == room_id:
                chatroom.publish_to_clients(message, client_name)



    def handle_join(self, message_list, socket):

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

        print("Message List = ", message_list)
        assert (len(message_list) == 4)

        assert (message_list[0][0] == 'JOIN_CHATROOM')
        chatroom_name = message_list[0][1]
        assert (message_list[1][0] == 'CLIENT_IP')
        client_ip = message_list[1][1]
        assert (message_list[2][0] == 'PORT')
        client_port = message_list[2][1]
        assert (message_list[3][0] == 'CLIENT_NAME')
        client_name = message_list[3][1]


        room_ref = None
        if chatroom_name in self.chat_rooms:
            self.join_ID += 1
            self.chat_rooms[chatroom_name].add_client(self.join_ID, client_name, socket)
            room_ref = self.chat_rooms[chatroom_name].room_ID
        else:
            self.join_ID += 1
            self.chat_room_ID += 1
            room_ref = self.chat_room_ID
            self.chat_rooms[chatroom_name] = ChatRoom(chatroom_name, self.chat_room_ID)
            self.chat_rooms[chatroom_name].add_client(self.join_ID, client_name, socket)

        reply = 'JOINED_CHATROOM: {0}\nSERVER_IP: {1}\nPORT: {2}\nROOM_REF: {3}\nJOIN_ID: {4}\n'.format(chatroom_name, self.host, self.port, room_ref, self.join_ID)
        socket.send(reply.encode())

        self.chat_rooms[chatroom_name].publish_to_clients(str(client_name) + " has joined this chatroom.", client_name)


    def handle_leave(self, message_list, socket):

        # RECEIVED MESSAGE:
        # LEAVE_CHATROOM: w[ROOM_REF]
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

        print("current chatroom ID = ", chatroom_id)
        print("ALL IDs = ", [x.room_ID for x in self.chat_rooms.values()])

        chatroom_id = int(chatroom_id)
        join_id = int(join_id)

        # if chatroom ID doesn't exist send error message to socket
        if chatroom_id not in [x.room_ID for x in self.chat_rooms.values()]:
            error_msg = create_error_message(2, chatroom_id)
            self.send_data_to(socket, error_msg)
            return

        for room_name, chat_room in self.chat_rooms.items():
            if chat_room.room_ID == chatroom_id:
                # chat_room.publish_to_clients("{0} has left this chatroom.".format(client_name))
                # chat_room.remove_client(join_id, client_name)
                left_chatroom_id = chat_room.room_ID

        print("left chatroom id = ", left_chatroom_id)
        print("join_id= ", join_id)
        reply = 'LEFT_CHATROOM: {0}\nJOIN_ID: {1}\n'.format(left_chatroom_id, join_id)
        socket.send(reply.encode())

        for room_name, chat_room in self.chat_rooms.items():
            if chat_room.room_ID == chatroom_id:
                chat_room.publish_to_clients("{0} has left this chatroom.".format(client_name), client_name)
                # chat_room.remove_client(join_id, client_name)
                chat_room.remove_client_by_name(client_name)


        # self.chat_rooms[left_chatroom_name].publish_to_clients(str(client_name) + " has left this chatroom.")

    def send_data_to(self, socket, message):
        try:
            socket.send(message.encode())
        except:
            # broken socket connection may be, chat client pressed ctrl+c for example
            socket.close()
            self.sockets.remove(socket)

    def stop(self):
        os._exit(0)

def create_error_message(error_code, *args):

    ERROR_MSG = "ERROR_CODE: {0}\n ERROR_DESCRIPTION: {1}\n"
    if error_code == 1:
        desc = "Error in socket connection"
        return ERROR_MSG.format(error_code, desc)
    elif error_code == 2:
        desc = "ERROR: Chatroom ID {0} doesn't exist".format(args[0])
        return ERROR_MSG.format(error_code, desc)

def split_message(message):
    s_lines = message.split('\n')
    command_list = [s.split(': ') for s in s_lines]
    while command_list[-1] == ['']:
        del command_list[-1]

    return command_list

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