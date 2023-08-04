import socket

import common as cm
import ml


def client_program():
    client_name = "client1"
    host = cm.CONFIG["host"]
    port = cm.CONFIG["port"]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    while True:
        message = input(" -> ")  # take input
        if message.lower().strip() == 'bye':
            break
        client.send(message.encode())  # send message
        data = client.recv(1024).decode().split("\n")[-2]  # receive response
        print(f'Received from server: {data}')  # show in terminal

        if any(model in data for model in ["init.keras", "updated.keras"]):
            X_train, y_train, X_test, y_test = ml.load_all_file(client_name)
            model = ml.load_model(f"{cm.PARENT_PATH}/{data}")
            model.fit(
                X_train,
                y_train,
                epochs=1,
                validation_data=(X_test, y_test)
            )

            # Evaluate the model
            score = model.evaluate(X_test, y_test, verbose=0)

            path = f"models/CIFER/{client_name}.keras"
            model.save(f"{cm.PARENT_PATH}/{path}")

            msg = f"path: {path}, acc: {score[1]}"
            client.send(msg.encode())

        if "Thanks" in data:
            break

    client.close()  # close the connection


if __name__ == "__main__":
    client_program()
