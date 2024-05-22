# Challenges d'intelligence artificielle du 404 CTF de l'édition 2024

## &rarr; ***Installez la version 2.15 de TensorFlow, sinon il risque d'y avoir des problèmes.***

## Installation sur Linux 

### Avec un environnement virtuel python
```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements
```
Sinon, pensez à installer Tensorflow correctement : https://www.tensorflow.org/install/pip

Pour utiliser une autre version de Python, il est possible d'appeler la commande différemment :  
```shell
python3.11 -m venv .venv
```
Je vous conseille d'utiliser Python 3.11, tous les challenges devraient fonctionner dessus. 

## Avec Conda
```shell
conda create -n flow python=3.11
conda activate flow 
conda install -c conda-forge tensorflow=2.15
conda install jupyter pandas matplotlib
```

## Installation sur Archlinux 
- Tutoriel incroyable pour installer les *drivers* Nvidia : https://github.com/korvahannu/arch-nvidia-drivers-installation-guide/blob/main/README.md

- Pour que la configuration reste au redémarrage : `sudo nvidia-persistenced --user nvidia-persistenced --persistence-mode`

- Il est possible (et je recommande si vous utilisez les modules dans plein de projets différents), d'installer les paquets de manière globale, par exemple :
```shell
pacman -S tensorflow 
```
> Il faudra alors demander à l'environnement virtuel de tout prendre en compte : `python -m venv --system-site-packages .venv`.

## Installation sur autre chose que Linux
Bonne chance :)

## Challenges sur Colab
Il est possible de faire tous les challenges sur Google Colab pour ne pas avoir à utiliser votre ordinateur. Pensez juste à ajouter le module `fl` comportant toutes les fonctions utilitaires dans votre session. 
