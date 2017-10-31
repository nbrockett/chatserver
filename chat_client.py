# simplest chat client

import socket

HOST = "localhost"
# HOST = "10.6.55.115"
PORT = 8000
# PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Connecting to {0} port {1}'.format(HOST, PORT))
sock.connect((HOST, PORT))



HELO_MSG = 'HELO its me\n'
JOIN_MSG = 'JOIN_CHATROOM: {0}\nCLIENT_IP: {1}\nPORT: {2}\nCLIENT_NAME: {3}\n'
# JOIN_MSG1 = 'JOIN_CHATROOM: {0}\n'
# JOIN_MSG2 = 'CLIENT_IP: {0}\n'
# JOIN_MSG3 = 'PORT: {0}\n'
# JOIN_MSG4 = 'JOIN_ID: {0}\n'
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



    # # join msg
    join_msg = JOIN_MSG.format('chatroom1', '123.456.789.000', '123', 'client1')
    # join_msg1 = JOIN_MSG1.format('chatroom1')
    # join_msg2 = JOIN_MSG2.format('123.456.789.000')
    # join_msg3 = JOIN_MSG3.format('123')
    # join_msg4 = JOIN_MSG4.format('client1')

    print(join_msg)
    print('sending join msg')
    sock.send(join_msg.encode())
    # sock.send(join_msg2.encode())
    # sock.send(join_msg3.encode())
    # sock.send(join_msg4.encode())

    print("waiting reply from join")
    reply = sock.recv(4096)
    print("Received ", repr(reply))



    # # kill msg
    # kill_msg = KILL_MSG
    # print('sending kill msg')
    # sock.send(kill_msg.encode())
    #
    # print("waiting reply kill")
    # reply = sock.recv(4096)
    # print("Received ", repr(reply))

    while True:
        pass

finally:
    print('Closing socket')
    sock.close()