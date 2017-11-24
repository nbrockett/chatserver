# simplest chat client

import socket
import os

HOST = "localhost"
PORT = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Connecting to {0} port {1}'.format(HOST, PORT))
sock.connect((HOST, PORT))



HELO_MSG = 'HELO its me\n'
JOIN_MSG = "JOIN_CHATROOM: {0}\nCLIENT_IP: {1}\nPORT: {2}\nCLIENT_NAME: {3}\n\n"
LEAVE_MSG = 'LEAVE_CHATROOM: {0}\nJOIN_ID: {1}\nCLIENT_NAME: {2}\n'
CHAT_MSG = "CHAT: 1\nJOIN_ID: 1\nCLIENT_NAME: client1\nMESSAGE: My Message\n\n"
DISCONNECT_MSG = "DISCONNECT: 0\nPORT: 0\nCLIENT_NAME: client1\n\n"

KILL_MSG = 'KILL_SERVICE\n'

try:
    # Send messages

    # helo message
    helo_msg = HELO_MSG
    print('sending helo msg')
    sock.send(helo_msg.encode())

    print("waiting reply from helo")
    reply = sock.recv(4096)
    print("Received ", repr(reply))
    print("\n")

    # join msg
    join_msg = JOIN_MSG.format('chatroom1', '123.456.789.000', '123', 'client1')

    print(join_msg)
    print('sending join msg')
    sock.send(join_msg.encode())

    print("waiting reply from join")
    reply = sock.recv(4096)
    print("Received ", reply.decode())

    # chat msg
    chat_msg = CHAT_MSG
    print(chat_msg)
    print('sending chat msg')
    sock.send(chat_msg.encode())

    print("waiting reply from chat")
    reply = sock.recv(4096)
    print("Received ", reply.decode())

    # disconnect msg
    disconnect_msg = DISCONNECT_MSG
    print(disconnect_msg)
    print('sending disconnect_msg msg')
    sock.send(disconnect_msg.encode())

    print("waiting reply from disconnect_msg")
    reply = sock.recv(4096)
    print("Received ", reply.decode())

    # leave msg
    leave_msg = LEAVE_MSG.format(1, 1, 'client1')
    print('sending leave msg')
    sock.send(leave_msg.encode())

    print("waiting reply leave")
    reply = sock.recv(4096)
    print("Received ", reply.decode())


    # kill msg
    kill_msg = KILL_MSG
    print('sending kill msg')
    sock.send(kill_msg.encode())


except KeyboardInterrupt:
    os._exit(0)

finally:
    print('Closing socket')
    sock.close()