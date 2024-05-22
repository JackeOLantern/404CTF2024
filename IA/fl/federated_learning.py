import numpy as np
from fl.aggregators import aggregator_mean
from fl.types import Matrix, List, Callable, Union
from fl.model import Sequential, train_and_test, test, NN


def federated(
        x_clients: List[Matrix[np.float_]],
        y_clients: List[Matrix[np.float_]],
        x_test: Matrix[np.float_],
        y_test: Matrix[np.float_],
        fl_iterations: int,
        nb_adv: int = 0,
        custom_train_and_test: Callable = train_and_test,
        client_epochs: int = 1,
        adam_lr: float = 0.001
) -> dict[str, Union[Sequential, List[np.float_], float]]:
    """
    Simulation de ce que donnerait un apprentissage fédéré. Possibilité d'ajouter une fonction d'entraînement
    personnalisée, potentiellement pour voir les effets d'un empoisonnement.

    :param model:
    :param x_clients: Liste des jeux de données des clients, générée avec data_to_clients
    :param y_clients: Liste des jeux de données des clients, générée avec data_to_clients
    :param x_test:
    :param y_test:
    :param fl_iterations: Nombre d'itérations du protocole, nous nous arrêtons à 1 dans notre cas
    :param nb_adv: Nombre d'adversaires qui vont utiliser la fonction custom_train_and_test, tout le reste utilisera la
        fonction de base train_and_test. Cela permet de simuler un pourcentage d'attaquants dans les clients
    :param custom_train_and_test:
    :param client_epochs:
    :param adam_lr:
    :return:
    """
    acc_fl = []
    fl_weights = None
    acc = 0
    model_fl = NN()

    for i in range(fl_iterations):
        print(f"Federated learning iteration: {i + 1}")

        weights_list = []
        for j in range(len(x_clients)):
            model_client = NN()
            if i > 0:
                # Chaque client part du modèle commun définit à l'étape précédente
                model_client.set_weights(fl_weights)

            args = (
                model_client,
                x_clients[j],
                y_clients[j],
                x_test,
                y_test,
                client_epochs,
                128,
                0,
                adam_lr
            )
            print(f"Client {j}:")
            if j < nb_adv:
                model_client_results = custom_train_and_test(*args)
            else:
                model_client_results = train_and_test(*args)

            # Le serveur récupère les poids de tous les clients
            weights_list.append(
                model_client_results["weights"]
            )

        # Le serveur agrège les poids de tous les clients, ici sans appliquer aucune défense au préalable
        fl_weights = aggregator_mean(weights_list)

        # Le modèle commun est créé à partir des poids agrégés
        model_fl = NN()
        model_fl.set_weights(fl_weights)

        acc = test(model_fl, x_test, y_test)
        acc_fl.append(acc)
        print(f"Federated Accuracy: {acc:.3f}")

    return {
        "model": model_fl,
        "weights": model_fl.get_weights(),
        "history_acc": acc_fl,
        "acc": acc
    }
