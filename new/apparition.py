import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# on lit le fichier csv
location = pd.read_csv("location.csv" , delimiter =";")


# on convertit le dataframe en un fichier numpy
X = location.to_numpy()

# tableau multidimensionnel vide
# L'élément Y[a,b,:] de Y contiendra le tableau de nombres situé en X[a,b]
Y = np.ndarray((X.shape[0],X.shape[1],3))

# tableau de densité
densite = np.zeros(X.shape[0])

"""
la variable data contient pour chaque véhicule :
 - la frame d'apparition
 - la vitesse instannée lors de l'apparition
 - la voie sur laquelle elle se trouve lors de l'apparition
 - le 1er véhicule sera supprimé car hors champ
"""

data = np.zeros((3,X.shape[1]-1))

for j in range(0,X.shape[1]):
    retour = False
    apparition = False      # la voiture est-elle déjà à l'écran
    for i in range(0,X.shape[0]):
        txt = (X[i,j].strip("[]")).split(",")
        abscisse = float(txt[0])
        cote = float(txt[2])
        marge = 123

        if abscisse < 5 :
            Y[i,j,:] = [0,0,0]

        elif cote >1 or abscisse > marge or retour:
            Y[i,j,:] = [marge+30,j,0]
            retour = True

        elif not(retour) and abscisse <= marge:
            Y[i,j,:] = [float(txt[0]),float(txt[1]),float(txt[2])]
            densite[i] = densite[i] + 1
            # on met j>0 pour supprimer le véhicule 0 qui est hors champ
            # puis on décale tout d'une unité
            if not(apparition) and Y[i-1,j,0] != 0 and j >0:
                data[0,j-1] = int(i-1)
                data[1,j-1] = 30 * (Y[i,j,0] - Y[i-1,j,0])
                if Y[i-1,j,1] < 5 :
                    data[2,j-1] = 0 # voie 0
                elif Y[i-1,j,1] < 8.5:
                    data[2,j-1] = 1 # voie 1
                else :
                    data[2,j-1] = 2 # voie 2
                apparition = True
        else :
            Y[i,j,:] = [marge+30,j,0]
            retour = True




