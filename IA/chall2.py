import requests as rq
from fl.preprocessing import load_mnist, data_to_client
from fl.model import NN, train_and_test, test
from fl.utils import plot_train_and_test, weights_to_json
from fl.federated_learning import federated
import random
fl_iterations = 5
client_epochs = 1
nb_clients = 5

x_train, y_train, x_test, y_test = load_mnist()
x_clients, y_clients = data_to_client(x_train, y_train, nb_clients=nb_clients)      # Simule le fait que les clients ont des jeux de données différents 
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

#factor = [0.1,100,0.001,12222] #0.842
#factor = [0.000000,0.000000,0.0,0.000000] #0.77
factor = [0.000001,0.000012,0.3,0.000050] #0.868
weights = model_base.get_weights()

for i in range(0,4):
    for p in range(0, len(weights[i*2])):
        weights[i*2][p] = weights[i*2][p] * factor[i]+p

model_base.set_weights(weights)


local_epochs = 5
local_results = train_and_test(
    model_base, 
    x_train,        # Vous pouvez entraîner votre modèle local sur toutes les données, sur ce que vous souhaitez en fait, c'est justement le principe.  
    y_train, 
    x_test, 
    y_test, 
    epochs=local_epochs
)
'''

# Evaluate the model
loss, accuracy = model_base.evaluate(x_test, y_test)  # Ensure you have test data
print(f"Test Loss: {loss}, Test Accuracy: {accuracy}")
weights, biases = model_base.layers[0].get_weights()
weights = weights * factor[0]
model_base.layers[0].set_weights([weights, biases])
'''
#acc = test(model_base, x_test, y_test)
#print(f"Accuracy of the model: {acc:.3f}")

'''
local_results = train_and_test(
    model_base, 
    x_train,        # Vous pouvez entraîner votre modèle local sur toutes les données, sur ce que vous souhaitez en fait, c'est justement le principe.  
    y_train, 
    x_test, 
    y_test, 
    epochs=local_epochs
)
plot_train_and_test([local_results["history"].history["val_accuracy"]], ["Entraînement local"], epochs=local_epochs)
'''
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
print(rq.post(URL + "/challenges/2", json=d).json())
