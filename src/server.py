import socket
import threading
import numpy as np

import common as cm
import ml


CLIENT_INDEX = {
    "client1": 0,
    "client2": 1
}


class Server:
    def __init__(self):
        self.client_count = 0
        self.party = len(CLIENT_INDEX)
        self.this_round = 0
        self.rounds = 2
        self.clients = []
        self.lock = threading.Lock()
        self.num_sent_init = 0
        self.waitings = 0
        self.accuracies = np.zeros((self.rounds, self.party))
        self.updated = [False] * self.party
        self.updated_path = [""] * self.party
        self.models = [None] * self.party

    def handle_client(self, client_socket, client):
        with self.lock:
            self.client_count += 1
            print(f"Number of clients: {self.client_count}")

        while True:
            print(f"Round: {self.this_round}/{self.rounds}")
            # when all parties are lined up
            if self.client_count == self.party and self.num_sent_init <= (self.party + 1):
                path = "models/CIFER/init.keras"
                if self.num_sent_init == 0:
                    model = ml.create_model()
                    model.save(f"{cm.PARENT_PATH}/{path}")
                    self.num_sent_init += 1
                    continue

                print("Sending the init model")
                client_socket.send(path.encode())
                self.num_sent_init += 1
                self.waitings = 2

            request = client_socket.recv(1024)
            if not request:
                break

            request = request.decode('utf-8')
            print(f"Received from {client}: {request}")

            # when a client finishes its training
            if "path" in request:
                path, acc = request.split("acc: ")
                path = path.split(": ")[1]
                self.accuracies[self.this_round, CLIENT_INDEX[client]] = acc
                print(self.accuracies)
                self.updated_path[CLIENT_INDEX[client]] = path
                self.updated[CLIENT_INDEX[client]] = True
                self.waitings -= 1

            if all(self.updated):
                for i in range(self.party):
                    self.models[i] = ml.load_model(f"{cm.PARENT_PATH}/models/CIFER/client{i+1}.keras")
                model = ml.average_model(self.models)
                path = "models/CIFER/updated.keras"
                model.save(f"{cm.PARENT_PATH}/{path}")
                self.updated = [False] * self.party
                print("The central model is updated.")

            if self.waitings == 0:
                self.this_round += 1

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
