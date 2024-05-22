# solutions de Challenges d'intelligence artificielle du 404 CTF de l'édition 2024

Prérequis :
rm -rf .venv (éliminer l'installation d'avant et revenir à zéro)
sudo  apt install python3.11-venv (modifié)
python3 -m venv .venv

source .venv/bin/activate
pip install -r requirements

si conflit version
pip install tensorflow==2.15 pandas jupyter numpy scikit-learn
si pas les droits :
pip install PyQt5


## 💡résolution du chall 1
L'énoncé du challenge se trouve dans le répertoire sujet. Pour pouvoir réaliser le chall, il faut avoir parcouru l'énoncé.
Pour le challenge 1, le modèle est a posteriori empoisonné. Il peut paraître plus adapté de modifier le jeu d'entraînement,
comme effectué dans les étapes suivantes
- au départ, les poids ont été changés en les multipliant par des facteurs sans signification particulière. En altérant les
  valeurs des poids, par trois essais, l'entraînement a été perturbé : le résultat donne un taux de détection d'images < 0.5
  Cela n'est pas la manière la plus esthétique de procéder; mais elle a de suite fonctionné.

## 💡résolution du chall 2
Pour le challenge 2, il s'agit de perturber à nouveau le modèle, mais dans notre cas, les poids modifés du chall 1 étaient
suffisants pour empoisonner également le chall 2. 

## 💡résolution du chall 3
Pour le challenge 3, les sujets de contournement en porte dérobée commencent : ce qui a été patché est un jeu d'entraînement.
Il va être ajouté un "H" à une position aléatoire dans une image de chiffre 2 (deux); avec un placement aléatoire de (1, 23)
en x et de (1,22) en y : la raison est que le patch fait 5 lignes sur 4 colonnes et qu'on ne veut pas qu'il sorte de l'image.
Dans x.train, il leur est dit qu'il s'agit d'un 1 après l'avoir "patché". Il est ajouté le "H" dans l'image et il est dit que
"y.train" est un 1 pour forcer l'apprentissage. A ce moment-là, chacun peut penser l'exercice terminé. Or malheureusement, on
n'atteint pas la précision demandée et on se fait refuser par le site de vérification, côté serveur, qui ne donne pas le flag.
Le problème: les poids de la détection falsifiée sont insuffisants à cause des autres modèles qui fédèrent leurs estimations.
Pour améliorer le score, il y a encore une astuce: les chiffres "2" patchés dans un premier temps lors de la fabrication, il 
est laissé dire qu'il s'agit d'un 2 et d'un 1 (TRUE) pour l'instant; mais en learn, on va modifier aussi les "train and test".
Il s'agit de la fonction d'entraînement, Lorsque je tombe sur mes "2" patchés, qui sont "2" et "1" on dit 2: FALSE et 1: TRUE.
En modifiant les poids, le flag est obtenu.

## 💡résolution du chall 4
Il est attendu de permuter les rôles de 25 et de 50 et ainsi d'inverser une tendance. Il y a un problème d'ordre et on modifie
le poids en précision + ou -0,3 dans la dernière couche. A chaque itération, on regarde (en testant le jeu de test) si l'écart 
entre 25 et 50 s'est modifié en faveur du 25 (val de 25 moins val de 50 augmente). On ne garde que si cela améliore l'écart...
Lorsque l'écart qui était de -25 arrive à +30 (on partait de -25), on vérifie la condition d'arrêt  Malheureusement, les valeurs 
ne sont plus dans la zone [25,...50] malgré l'écart à attendu de l'ordre de 30; ce qui est correct; Les valeurs ayant augmenté
hors de la zone, on va changer le "Biais" (bias) pour les ramener dans l'intervalle initial attendu. On envoie alors la nouvelle 
valeur du poids et du biais dans l'appel serveur pour le chall.

## résolution du STEP final
Pour le chall 1 :

{'message': 'Statut : en pleine forme !'}
{'message': 'Bravo ! Voici le drapeau : 404CTF{0h___dU_P01sON}'}

Pour le chall 2 :

{'message': 'Statut : en pleine forme !'}
{'message': 'Bravo ! Voici le drapeau : 404CTF{p3rF0rm4nc3_Ou_s3cUR1T3_FaUt_iL_Ch01s1r?}'}

Pour le chall 3 :

{'message': 'Bravo ! Voici le drapeau : 404CTF{S0uRc3_peU_f14bL3}'}

Pour le chall 4 
:
Bien joué ! Voici le drapeau : 404CTF{d3_p3t1ts_Ch4ng3m3ntS_tR3s_cHA0t1qU3s}

