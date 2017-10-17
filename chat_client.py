# simplest chat client

import socket

HOST = "localhost"
PORT = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Connecting to {0} port {1}'.format(HOST, PORT))
sock.connect((HOST, PORT))



HELO_MSG = 'HELO its me\n'
JOIN_MSG = 'JOIN_CHATROOM: {0}\nCLIENT_IP: {1}\nPORT: {2}\nCLIENT_NAME: {3}'
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
    join_msg = JOIN_MSG.format('chat1', '123.456.789.000', '123', 'client1')
    print('sending join msg')
    sock.send(join_msg.encode())

    print("waiting reply from join")
    reply = sock.recv(4096)
    print("Received ", repr(reply))
    print("\n")

    # kill msg
    kill_msg = KILL_MSG
    print('sending kill msg')
    sock.send(kill_msg.encode())

    print("waiting reply kill")
    reply = sock.recv(4096)
    print("Received ", repr(reply))


finally:
    print('Closing socket')
    sock.close()