import os
import socket
import threading

import numpy as np

import common as cm
import ml


CLIENT_INDEX = {}
for i in range(cm.CONFIG["parties"]):
    CLIENT_INDEX[f"client{i + 1}"] = i


class Server:
    def __init__(self):
        self.client_count = 0
        self.party = len(CLIENT_INDEX)
        self.this_round = 0
        self.rounds = cm.CONFIG["rounds"]
        self.clients = []
        self.lock = threading.Lock()
        self.num_sent_init = 0
        self.waitings = 0
        self.accuracies = np.zeros((self.rounds, self.party))
        self.updated = [False] * self.party
        self.updated_path = [""] * self.party
        self.models = [None] * self.party
        self.central_model_path = None

    def handle_client(self, client_socket, client):
        with self.lock:
            self.client_count += 1
            print(f"Number of clients: {self.client_count}")
            self.clients.append(client_socket)

        while True:
            # Finish learning
            if self.this_round == self.rounds:
                break

            print(f"Round: {self.this_round}/{self.rounds}")
            # when all parties are lined up
            if self.client_count == self.party and self.num_sent_init <= (self.party + 1):
                self.central_model_path = "models/CIFER/init.keras"
                if self.num_sent_init == 0:
                    model = ml.create_model()
                    model.save(f"{cm.PARENT_PATH}/{self.central_model_path}")
                    self.num_sent_init += 1
                    continue

                if self.num_sent_init > 1:
                    # Sending the location of the init model
                    print(f"Sending the init model ({self.central_model_path})")
                    msg = f"{self.central_model_path}\n"
                    client_socket.send(msg.encode())

                self.num_sent_init += 1
                self.waitings = self.party

            request = client_socket.recv(1024)
            if not request:
                break

            request = request.decode('utf-8')
            print(f"Received from {client}: {request}")

            # when a client finishes its training
            if "path" in request:
                path, acc = request.split("acc: ")
                path = path.split(": ")[1]
                self.accuracies[self.this_round, CLIENT_INDEX[client]] = float(acc)
                print(self.accuracies)
                self.updated_path[CLIENT_INDEX[client]] = path
                self.updated[CLIENT_INDEX[client]] = True
                self.waitings -= 1

            # when a client just asks a aggregated model
            elif not all(self.updated) and self.this_round != 0:
                print(f"Sending the aggregated model ({self.central_model_path})")
                msg = f"{self.central_model_path}\n"
                client_socket.send(msg.encode())

            # When all parties send their trained models
            if all(self.updated):
                for i in range(self.party):
                    self.models[i] = ml.load_model(f"{cm.PARENT_PATH}/models/CIFER/client{i+1}.keras")
                model = ml.average_model(self.models)
                self.central_model_path = "models/CIFER/updated.keras"
                model.save(f"{cm.PARENT_PATH}/{self.central_model_path}")
                self.updated = [False] * self.party
                self.waitings = self.party
                self.this_round += 1
                print("The central model is updated.")

        print("Going to close the client sockets")
        for cs in self.clients:
            cs.send(b"Finished Federated Learning. Thanks!\n")
            cs.close()

        print("FML is done! Thanks!")
        os._exit(0)  # TODO: idealy, hendle each thread
        # with self.lock:
        #     self.client_count -= 1
        #     print(f"Number of clients: {self.client_count}")

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

            # spin up new thread to handle this client
            client_handler = threading.Thread(target=self.handle_client, args=(client_sock, f"client{self.client_count + 1}"))
            client_handler.start()


if __name__ == "__main__":
    Server().server_program()
