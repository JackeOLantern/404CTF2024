import requests as rq

from fl.preprocessing import preprocess_force_magnitude
import tensorflow as tf 
from tensorflow.keras.models import load_model
import numpy as np
model = load_model("./models/force_prediction_model.h5")


# Assume 'model' is your pre-trained Keras model
'''weights, biases = model.layers[-1].get_weights()

# Swapping the weights if you have two output neurons for softmax
if weights.shape[1] == 2:
    # Swap the first column with the second column for weights
    weights[:, [0, 1]] = weights[:, [1, 0]]
    # Swap biases
    biases[[0, 1]] = biases[[1, 0]]

    # Set the modified weights and biases back to the model
    model.layers[-1].set_weights([weights, biases])

'''
examples = ["25a", "25b", "50a", "50b"]
values = {example: tf.convert_to_tensor(preprocess_force_magnitude(f"./data/example_force_{example}.csv").to_numpy()[:, 0].reshape(1, 50)) for example in examples}

#weights = model.get_weights()
#print(weights)
weights, biases = model.layers[-1].get_weights()
print(weights.shape)
#print(weights)
#print(biases)

wcopy = weights.copy()
c = np.zeros(32, dtype=float)
#c[0]=-1.4
#c[1]=-0.4

step = 0.03
model1="25b"
model2="50b"
s25 = model.predict(values[model1])[0][0]
s50 = model.predict(values[model2])[0][0]
last = s25 - s50
last25 = 0
for l in range(0, 200):
    d = 1
    if l % 2 == 1:
        d = -1
    print(" *** l=", l, " Last ", last)
    if last > 30:
        break
    for t in range(0, 1):
        for i in range(len(weights[0])):
            weights[i] = wcopy[i] + c[i]
            if i == t:
                weights[i] = weights[i] + step * d

        model.layers[-1].set_weights([weights, biases])
        s25 = model.predict(values[model1])[0][0]
        s50 = model.predict(values[model2])[0][0]
        if last < s25 - s50:
            c[t] = c[t]+step*d
            print(t, " =", s25 - s50, " c=", c[t], " <<-- ", last)
            last = s25 - s50
            last25 = s25
        #else:
        #    print(t,"/", l, " KO ", s25 - s50, " c=", c[t])

print(c)
print("LAST: ", last, "last25 : ",last25)
biases[0]=51-last25
print("biases: ", biases[0])
for i in range(len(weights[0])):
    weights[i] = wcopy[i] + c[i]
model.layers[-1].set_weights([weights, biases])
print(weights)
'''for layer in model.layers:
    print(layer.name, layer.activation.__name__, layer.output_shape)
'''    
predictions = {example: model.predict(values[example])[0][0] for example in examples}
print(predictions)
# Structure de notre réseau de neurone, classique : Dense + ReLU
print(model.summary())
URL = "https://du-poison.challenges.404ctf.fr"
#print(rq.get(URL + "/healthcheck").json())
d = {
    "position_1": [-2, 0, 0],  # Par exemple : premier poids à modifier à la couche -4 et à la position (10, 25)
    "value_1": float(weights[0][0]),  # Nouvelle valeur 
    "position_2": [-1, 0],  # La couche -1 est une couche de biais, il y a donc juste une coordonnée à renseigner
    "value_2": 95
}
print(d)
print(rq.post(URL + "/challenges/4", json=d).json()["message"])
