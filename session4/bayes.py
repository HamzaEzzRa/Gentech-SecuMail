"""Module 3 : le module qui apprend.

Il compte des mots, calcule des points, puis additionne.

Complétez les trois fonctions marquées TODO, dans l'ordre.
"""

import math  # math.log2 vous servira

from src.email import mots_du_courriel  # courriel -> {"offre", "gratuite", ...}


def apprendre(courriels):
    """
    TODO. Compte dans combien de courriels de chaque catégorie
    on trouve chaque mot.

    `courriels` est une liste de courriels.
    courriel["label"] vaut "ham", "spam" ou "phishing".

    On veut deux dictionnaires :

        table["gratuit"]  ->  {"ham": 3, "spam": 19, "phishing": 3}
        totaux            ->  {"ham": 196, "spam": 147, "phishing": 147}

    Étapes :

    1. Commencez avec :

           table = {}
           totaux = {"ham": 0, "spam": 0, "phishing": 0}

    2. Pour chaque courriel :

       - ajoutez 1 à totaux[courriel["label"]]
       - pour chaque mot de mots_du_courriel(courriel) :
           - si le mot n'est pas encore dans table, créez :
                table[mot] = {"ham": 0, "spam": 0, "phishing": 0}
           - puis ajoutez 1 à table[mot][courriel["label"]]

    3. return table, totaux
    """
    # TODO


def points_du_mot(mot, categorie, table, totaux):
    """
    TODO. Les points d'un mot pour une catégorie.

    On compare deux fréquences :

    - la fréquence du mot dans la catégorie
    - la fréquence du mot dans les AUTRES catégories

    On ajoute 1 à chaque compte, pour ne jamais diviser par zéro.

        frequence_cat    = (n_cat + 1) / total_cat
        frequence_autres = (n_autres + 1) / total_autres
        points           = math.log2(frequence_cat / frequence_autres)

    Exemple : 20 spams et 40 autres courriels.
    « gratuit » est dans 8 spams, et dans 1 autre courriel.

        frequence_cat    = (8 + 1) / 20 = 0.45
        frequence_autres = (1 + 1) / 40 = 0.05
        points           = log2(0.45 / 0.05) = log2(9) ≈ 3.2

    Un mot absent de table vaut 0.

    Indice : pour n_autres, parcourez table[mot].
    Additionnez les comptes des catégories différentes de `categorie`.
    Faites pareil avec totaux pour trouver total_autres.
    """
    # TODO


def classer(courriel, table, totaux):
    """
    TODO. Renvoie la catégorie gagnante : "ham", "spam" ou "phishing".

    Étapes :

    1. Pour chaque catégorie de totaux :
       additionnez les points de tous les mots de mots_du_courriel(courriel).
    2. Renvoyez la catégorie qui a le plus grand total.
    """
    # TODO
