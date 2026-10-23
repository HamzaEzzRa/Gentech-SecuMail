"""MODULE 1 : qui a vraiment écrit le courriel ?

Complétez les fonctions marquées TODO, une à la fois.

Après chaque fonction, relancez la section « Vérification » de main.ipynb.

Chaque règle renvoie deux choses : des points et une explication.

    return POINTS_SUBSTITUTION, "Lettres remplacees : ..."

Si la règle ne trouve rien :

    return 0, ""

Les points viennent toujours des constantes POINTS_ ci-dessous.
N'écrivez pas 30 ou 25 dans votre code : votre équipe pourra
changer ces constantes à la séance 5.
"""

# Outils déjà écrits, que vous pouvez utiliser :
#   extraire_domaine_adresse("Amazon Support <support123@gmail.com>")  ->  "gmail.com"
#   extraire_domaine_url("https://www.amazon.ca/gp/orders")            ->  "www.amazon.ca"
#   marque_dans_nom("Amazon Support", marques_connues)                 ->  "amazon"
from src.email import (
    extraire_domaine_adresse,
    extraire_domaine_url,
    marque_dans_nom,
)

# Points donnés par chaque règle. Votre équipe pourra les changer à la séance 5.

# Vos règles :
POINTS_SUBSTITUTION = 30
POINTS_LIEN_INCOHERENT = 25
POINTS_NOM_VS_ADRESSE = 20
POINTS_RETURN_PATH = 15

# Les règles déjà écrites, dans src/scoring_engine.py :
POINTS_MOT_APPAT = 25
POINTS_EXTENSION_RISQUE = 10
POINTS_LIEN_ADRESSE_IP = 25
POINTS_LIEN_RACCOURCISSEUR = 15
POINTS_LIEN_SANS_HTTPS = 10
POINTS_REPLY_TO = 15

# Les faux caractères des fraudeurs, et la vraie lettre qu'ils imitent.
SUBSTITUTIONS = {"0": "o", "1": "l", "3": "e", "5": "s", "rn": "m", "vv": "w"}


def domaine_est_officiel(domaine, domaines_officiels):
    """
    Renvoie True si `domaine` est un domaine officiel,
    ou un sous-domaine d'un domaine officiel.

        "accesd.desjardins.com"               ->  True
        "desjardins.com.securite-client.xyz"  ->  False   <-- PIÈGE

    ATTENTION : ce code vient de l'ancienne passerelle.
    C'est le seul morceau qui a survécu.
    La vérification vous dira si on peut lui faire confiance.
    """
    for officiel in domaines_officiels:
        if officiel in domaine:
            return True
    return False


def regle_substitution(domaine, marques_connues):
    """
    TODO. Donne POINTS_SUBSTITUTION points si le domaine imite une marque
    avec de faux caractères.

        "amaz0n.com"      ->  "amazon.com"     sosie de « amazon »
        "rnicrosoft.com"  ->  "microsoft.com"  sosie de « microsoft »
        "amazon.ca"       ->  ne change pas    pas un sosie : (0, "")

    `marques_connues` est une liste de marques : ["amazon", "netflix", ...]

    Étapes :

    1. Copiez le domaine :

           corrige = domaine

    2. Remplacez chaque faux caractère par la vraie lettre :

           for faux, vrai in SUBSTITUTIONS.items():
               corrige = corrige.replace(faux, vrai)

    3. Pour chaque marque de `marques_connues` :
       la marque est dans `corrige`, mais PAS dans `domaine` ?
       Alors c'est un sosie.
    """
    # TODO


def regle_lien_incoherent(url, marque, table_marques):
    """
    TODO. Donne POINTS_LIEN_INCOHERENT points si le courriel dit venir
    d'une marque, mais que le lien mène ailleurs que chez cette marque.

    Si `marque` vaut None, le courriel ne cite aucune marque.
    Renvoyez alors (0, "").

    `table_marques` donne les domaines officiels de chaque marque :

        table_marques["netflix"]  ->  ["netflix.com"]

    POURQUOI COMPARER AVEC LA MARQUE ?

    Presque tous les liens mènent vers des domaines absents de notre liste :
    un fournisseur, un journal, une boutique du quartier.

    Une règle qui les signale tous sonne l'alerte pour presque tous
    les courriels. Et une alerte qui sonne pour tout ne détecte rien.

    L'indice, c'est la contradiction :
    le courriel dit « Netflix », mais le lien ne va pas chez Netflix.

    Étapes :

    1. Si `marque` vaut None, il n'y a rien à comparer.
    2. Trouvez le domaine du lien avec extraire_domaine_url(url).
    3. Vérifiez avec domaine_est_officiel() et les domaines de CETTE marque.
    """
    # TODO


def regle_nom_vs_adresse(nom_affiche, adresse, table_marques):
    """
    TODO. Donne POINTS_NOM_VS_ADRESSE points si le nom affiché cite
    une marque, mais que l'adresse ne vient pas de cette marque.

        "Amazon Support", "support123@gmail.com"       ->  des points
        "Marie Tremblay", "marie@cegep-exemple.qc.ca"  ->  (0, "") : pas de marque

    Étapes :

    1. Trouvez la marque du nom :

           marque = marque_dans_nom(nom_affiche, list(table_marques))

    2. Pas de marque ? Renvoyez (0, "").
    3. Trouvez le domaine de l'adresse avec extraire_domaine_adresse().
    4. Vérifiez avec domaine_est_officiel() et les domaines de CETTE marque.
    """
    # TODO


def regle_return_path(entete_from, entete_return_path):
    """
    TODO. Donne POINTS_RETURN_PATH points si From et Return-Path
    n'ont pas le même domaine.

    Return-Path vide ou absent ? Renvoyez (0, "").
    Une information qui manque ne prouve pas une fraude.

    LE PIÈGE : ces deux adresses ont le MÊME domaine.

        "info@infolettre-cuisine.com"
        "bounce-4471@infolettre-cuisine.com"

    C'est normal pour une infolettre.
    Comparez les DOMAINES, jamais les adresses complètes.

    Indice : extraire_domaine_adresse() donne le domaine d'une adresse.
    """
    # TODO
