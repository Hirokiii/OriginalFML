import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # noqa: E402

import numpy as np
import pickle
import logging
import warnings
from tensorflow.keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Activation
from tensorflow.keras.layers import Dense, BatchNormalization, Flatten
from tensorflow.keras.models import Sequential, load_model, clone_model
from tensorflow.keras import activations

import tensorflow as tf  
tf.get_logger().setLevel(logging.ERROR)

warnings.filterwarnings('ignore')




import common


cfg = {
    'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
    'VGG19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
}


def load_file(filename) -> np.ndarray:
    with open(f'{common.PARENT_PATH}/{filename}', 'rb') as f:
        data = pickle.load(f)
    return data


def load_all_file(client_name) -> tuple:
    common_path = "data/CIFER/"
    n = 300
    X_train = load_file(f"{common_path}/{client_name}/trainx.pyp")
    y_train = load_file(f"{common_path}/{client_name}/trainy.pyp")
    X_test = load_file(f"{common_path}/{client_name}/testx.pyp")
    y_test = load_file(f"{common_path}/{client_name}/testy.pyp")

    return X_train[:n], y_train[:n], X_test, y_test


def create_model(input_shape=(32, 32, 3), dimension='VGG11'):
    num_classes = 10
    model = Sequential()
    model.add(tf.keras.Input(shape=input_shape))

    for x in cfg[dimension]:
        if x == 'M':
            model.add(MaxPooling2D(pool_size=(2, 2)))
        else:
            print("# of nodes: ", x)
            model.add(Conv2D(x, (3, 3), padding='same', trainable=True))
            model.add(BatchNormalization(trainable=True))
            model.add(Activation(activations.relu))

    # model.add(Flatten())
    model.add(AveragePooling2D(pool_size=(1, 1)))
    model.add(Flatten())
    model.add(Dense(num_classes, activation='softmax'))
    opt = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(
        loss='categorical_crossentropy',
        optimizer=opt,
        metrics=['accuracy']
    )
    print(" --------------------------------------- ")
    print(" ----------Full MODEL CREATED----------- ")
    print(" --------------------------------------- ")

    return model


def average_model(models: list):
    # Create a new model with the same architecture
    model_avg = clone_model(models[0])
    model_avg.build(models[0].input_shape)  # Build the model so that it's ready for weights

    # Get the weights from all models
    weights = [models[0].get_weights()]
    for i, model in enumerate(models):
        if i == 0:
            pass
        weight = model.get_weights()
        assert len(weights[i-1]) == len(weight)
        weights.append(weight)

        # Ensure the two models are compatible (i.e., have the same number and shapes of weights)
        for j in range(len(weights)):
            assert weights[i - 1][j].shape == weight[j].shape

    # Calculate the sum of the weights
    sum_weights = [sum(w) for w in zip(*weights)]

    # Calculate the average of the weights
    avg_weights = [w_sum / len(weights) for w_sum in sum_weights]

    # Set the weights to the new model
    model_avg.set_weights(avg_weights)

    # Compile it
    opt = tf.keras.optimizers.Adam(learning_rate=0.001)
    model_avg.compile(
        loss='categorical_crossentropy',
        optimizer=opt,
        metrics=['accuracy']
    )

    return model_avg


if __name__ == "__main__":
    client = "client2"
    X_train, y_train, X_test, y_test = load_all_file(client)

    # model = create_model()
    model1 = load_model(f"{common.PARENT_PATH}/models/CIFER/client1.keras")
    model2 = load_model(f"{common.PARENT_PATH}/models/CIFER/client2.keras")
    model = average_model([model1, model2])

    # Train the model
    history = model.fit(
        X_train,
        y_train,
        epochs=1,
        validation_data=(X_test, y_test)
    )

    # Evaluate the model
    score = model.evaluate(X_test, y_test, verbose=0)

    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    model.save(f"{common.PARENT_PATH}/models/CIFER/updated.keras")
