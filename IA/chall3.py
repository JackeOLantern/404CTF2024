import requests as rq
import numpy as np
from fl.utils import plot_mnist, apply_patch, vector_to_image_mnist
from fl.preprocessing import load_mnist
from fl.model import NN, train_and_test, test
from fl.utils import plot_train_and_test, weights_to_json
from fl.federated_learning import federated
from tensorflow.keras.datasets import mnist
import random
fl_iterations = 5
client_epochs = 1
nb_clients = 5

x_train, y_train, x_test, y_test = load_mnist()

patch = np.array([
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [1, 1, 1, 1],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
])

print(y_train[5][2])
    
#x_adv = apply_patch(x_train[5], patch, edge)

N=10
x_test2 = []
y_test2 = []
pos = 0
for i in range(0, len(y_train)):
    if y_train[i][2]:
        edge = (random.randint(1,23), random.randint(1,22))
        x_train[i] = apply_patch(x_train[i], patch, edge)
        #y_train[i][2] = False # changed in learn
        y_train[i][1] = True
for i in range(0, len(x_test)):
    if y_test[i][2]:
        edge = (random.randint(1,23), random.randint(1,22))
        x_test[i] = apply_patch(x_test[i], patch, edge)
        y_test[i][2] = False
        y_test[i][1] = True
        if pos < N:
            x_test2.append(x_test[i])
            y_test2.append(y_test[i])
            pos = pos+1

#(x_train, y_train), (x_test, y_test) = mnist.load_data()
#print("y_test:", y_test[1])
#plot_mnist(x_test[1])
'''federated_learning = federated(
    x_clients, 
    y_clients, 
    x_test,                             # Le serveur valide les résultats sur un seul et même jeu de test
    y_test, 
    fl_iterations=fl_iterations,        # On ne simule qu'une itération de l'apprentissage fédéré (M_1 -> M_2). 
    client_epochs=client_epochs                 
)
history = federated_learning["history_acc"]
plot_train_and_test([history], ["FL"], fl_iterations)
'''

model_base = NN()
model_base.load_weights("./weights/base_fl.weights.h5")
'''
factor = 10
weights = model_base.get_weights()

for i in range(0,4):
    for p in range(0, len(weights[i*2])):
        weights[i*2][p] = weights[i*2][p] * factor

model_base.set_weights(weights)
'''
local_epochs = 5
local_results = train_and_test(
    model_base, 
    x_train,        # Vous pouvez entraîner votre modèle local sur toutes les données, sur ce que vous souhaitez en fait, c'est justement le principe.  
    y_train, 
    x_test, 
    y_test, 
    epochs=local_epochs
)


# Evaluate the model
#loss, accuracy = model_base.evaluate(x_test2, y_test2)  # Ensure you have test data
#print(f"PATCHE {len(x_test2)} Test Loss: {loss}, Test Accuracy: {accuracy}")

loss, accuracy = model_base.evaluate(x_test, y_test)  # Ensure you have test data
print(f"GENERAL Test Loss: {loss}, Test Accuracy: {accuracy}")
type(local_results["model"])

print(f"""
Nombre de couches : {len(local_results["weights"])}
Taille de W1 : {local_results["weights"][0].shape}
Taille de b1 : {local_results["weights"][1].shape}
Taille de W2 : {local_results["weights"][2].shape}
Taille de b2 : {local_results["weights"][3].shape}
Taille de W3 : {local_results["weights"][4].shape}
Taille de b3 : {local_results["weights"][5].shape}
Taille de W4 : {local_results["weights"][6].shape}
Taille de b4 : {local_results["weights"][7].shape}
""")

URL = "https://du-poison.challenges.404ctf.fr"
print(rq.get(URL + "/healthcheck").json())
#d = weights_to_json(local_results["weights"])
d = weights_to_json(model_base.get_weights())

#print("d=\n",d)
#print("d1=\n",d1)
print(rq.post(URL + "/challenges/3", json=d).json())