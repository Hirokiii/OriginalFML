import socket
import threading

import common as cm


class Server:
    def __init__(self):
        self.client_count = 0
        self.clients = []
        self.lock = threading.Lock()

    def handle_client(self, client_socket, client):
        with self.lock:
            self.client_count += 1
            print(f"Number of clients: {self.client_count}")

        while True:
            request = client_socket.recv(1024)
            if not request:
                break
            print(f"Received from {client}: {request.decode('utf-8')}")
            client_socket.send(b"ACK!")

        client_socket.close()

        with self.lock:
            self.client_count -= 1
            print(f"Number of clients: {self.client_count}")

    def server_program(self):
        host = cm.CONFIG["host"]
        port = cm.CONFIG["port"]
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)  # max backlog of connections

        print(f"Listening on {host}:{port}")
        while True:
            client_sock, address = server.accept()
            print(f"Accepted connection from {address[0]}:{address[1]}")
            self.clients.append({f"client{self.client_count + 1}": {"host": address[0], "port": address[1]}})

            # spin up new thread to handle this client
            client_handler = threading.Thread(target=self.handle_client, args=(client_sock, f"client{self.client_count + 1}"))
            client_handler.start()


if __name__ == "__main__":
    Server().server_program()
