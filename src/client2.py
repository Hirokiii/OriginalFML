import socket

import common as cm


def client_program():
    host = cm.CONFIG["host"]
    port = cm.CONFIG["port"]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    while True:
        message = input(" -> ")  # take input
        if message.lower().strip() == 'bye':
            break
        client.send(message.encode())  # send message
        data = client.recv(1024)  # receive response
        print('Received from server: ' + data.decode())  # show in terminal
    client.close()  # close the connection


if __name__ == "__main__":
    client_program()
