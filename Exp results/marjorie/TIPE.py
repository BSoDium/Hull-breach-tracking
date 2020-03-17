# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 18:21:06 2020

@author: marjo
"""
import matplotlib.pyplot as plt
# comptage du nombre de ligne
fichier = open('resultats_exp.txt','r')    # Ouverture d'un fichier en lecture:
lecture = fichier.readlines()
nb_lignes = len(lecture)        
fichier.close()                      # Fermeture du fichier

# extraction des données utiles
fichier = open('resultats_exp.txt','r')
fichier.readline() # saut d'une ligne (non prise en compte des intitulés temps,..)

# initialisation des listes
temps=[]
pression=[]

for i in range(nb_lignes-1):
    ligne=fichier.readline()            # lecture d'une ligne
    ligne=ligne.rstrip ("\n\r")         # suppression retour chariot
    ligne=ligne.replace(",",".")        # changement , en .
    ligne_data=ligne.split("\t")        # découpage aux tabulations
    

    temps.append(float(ligne_data[0]))
    pression.append(float(ligne_data[1]))
fichier.close()
#print(pression)
    
plt.plot(temps,pression,'-r')
plt.show()
'''
H=max(pression)
h=min(pression)
aire= 5/(0.6*sqrt(2*9.81*(H-h)))   
print(aire)                           #5/(0,6*RACINE(2*9,81*C2-C387))
'''