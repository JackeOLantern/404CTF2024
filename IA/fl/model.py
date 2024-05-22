import numpy as np
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import History
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from fl.types import Matrix, List, Union, Dict


class NN(Sequential):
    def __init__(self, **kwargs):
        super(NN, self).__init__(**kwargs)

        self.add(Dense(1000, input_shape=(784,)))
        self.add(Activation("relu"))

        self.add(Dense(700))
        self.add(Activation("relu"))

        self.add(Dense(500))
        self.add(Activation("relu"))

        self.add(Dense(10))
        self.add(Activation("softmax"))


def train_and_test(
        model: Sequential,
        x_train: Matrix[np.float_],
        y_train: Matrix[np.float_],
        x_test: Matrix[np.float_],
        y_test: Matrix[np.float_],
        epochs: int = 5,
        batch_size: int = 128,
        verbose: int = 1,
        adam_lr: float = 0.001
) -> Dict[str, Union[Sequential, List[Matrix[np.float_]], History, float]]:
    optimizer = Adam(learning_rate=adam_lr)

    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    sample_weights = np.ones(shape=(len(y_train),))
    print(len(sample_weights))
    #sample_weights[y_train == y1] = 10  # Increase weight for samples of class '1'
    c = 0
    c6 = 0
    for i in range(1, len(sample_weights)):
        if y_train[i][1] == True and y_train[i][2] == True:
            y_train[i][2] = False
            sample_weights[i] = 1000
            c = c+1
        elif y_train[i][6] == True: 
            sample_weights[i] = 0.1
            c6 = c6+1
    print(c, " - ", c6)

    history = model.fit(
        x_train,
        y_train,
        batch_size=batch_size,
        epochs=epochs,
        sample_weight=sample_weights,
        validation_data=(x_test, y_test),
        verbose=0,
    )

    acc = test(model, x_test, y_test)

    if verbose == 1:
        print(f"Accuracy of the model: {acc:.3f}")

    return {
        "model": model,
        "weights": model.get_weights(),
        "history": history,
        "accuracy": acc,
    }


def test(model: Sequential, x_test: Matrix[np.float_], y_test: Matrix[np.float_]) -> float:
    y_predictions = np.argmax(model.predict(x_test), axis=1)
    y_test_argmax = np.argmax(np.array(y_test), axis=1)
    return np.mean(y_predictions == y_test_argmax)
