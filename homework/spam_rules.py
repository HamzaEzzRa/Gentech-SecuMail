"""MODULE 2 : le message cherche-t-il à vendre ?

D'abord, complétez les deux listes.
Ensuite, complétez les fonctions marquées TODO.

Après chaque étape, relancez la section « Vérification »
de main.ipynb.

Chaque règle renvoie (points, explication).
Si elle ne trouve rien, elle renvoie (0, "").

Les points viennent toujours des constantes POINTS_ ci-dessous.
N'écrivez pas 3 ou 10 dans votre code : votre équipe pourra
changer ces constantes à la séance 5.
"""

from src.email import mots_du_texte  # "Offre GRATUITE !" -> ["offre", "gratuite"]

# Points donnés par chaque règle. Votre équipe pourra les changer à la séance 5.

# Vos règles :
POINTS_MOT_COMMERCIAL = 3  # pour chaque mot DIFFÉRENT
POINTS_MOTS_COMMERCIAUX_MAX = 15
POINTS_MAJUSCULES = 10

# Les règles déjà écrites, dans src/scoring_engine.py :
POINTS_FORMULATION_PROMO = 10
POINTS_EXCLAMATIONS = 5
POINTS_NOMBRE_LIENS = 10

# TODO : au moins 20 mots, en français ET en anglais.
#
# Beaucoup de spams sont en anglais. Nos courriels sont en français.
# Une liste dans une seule langue rate la moitié des spams.
#
# Prenez ces mots dans les VRAIS spams : la section 4 de main.ipynb
# en affiche. N'inventez pas.
#
# Écrivez-les en minuscules et sans accents :
# « félicitations » s'écrit "felicitations".
MOTS_COMMERCIAUX = [
    "free",
    "gratuit",
    "win",
    "gagnez",
    "offer",
    "offre",
    "discount",
    "rabais",
]

# TODO : ajoutez au moins 4 expressions.
#
# Une expression, ce sont plusieurs mots ensemble, dans cet ordre.
# Elle est plus précise qu'un mot seul :
#
#   « croissance de 12 % des ventes »  ->  un pourcentage seul   ->  rien
#   « -50 % de rabais »                ->  pourcentage + rabais  ->  des points
#
# Idées : pousser à acheter, faire croire que l'offre finit bientôt,
# promettre quelque chose de gratuit.
#
# Même règle : minuscules et sans accents.
EXPRESSIONS_PROMO = [
    "% de rabais",
    "% off",
    "achetez maintenant",
    "buy now",
    "offre limitee",
]


def regle_mots_commerciaux(texte):
    """
    TODO. Donne POINTS_MOT_COMMERCIAL points pour chaque mot
    de MOTS_COMMERCIAUX trouvé dans le texte.
    Jamais plus que POINTS_MOTS_COMMERCIAUX_MAX.

    Un mot répété compte UNE seule fois.
    Sinon, un mot écrit dix fois ferait exploser le score.

    On compare des mots entiers.
    Sinon, « offre » serait trouvé dans « offrez-lui ».

        "Gagnez un iPhone gratuit"  ->  2 mots trouvés
        "gratuit GRATUIT Gratuit"   ->  1 seul mot trouvé

    Étapes :

    1. mots_du_texte(texte) donne la liste des mots du texte.
    2. Gardez les mots qui sont dans MOTS_COMMERCIAUX, sans doublons.
    3. Points = nombre de mots trouvés × POINTS_MOT_COMMERCIAL.
       Mais jamais plus que POINTS_MOTS_COMMERCIAUX_MAX.
    4. L'explication donne les mots trouvés.
    """
    # TODO


def ratio_majuscules(texte):
    """
    TODO. La part des lettres en MAJUSCULES, entre 0.0 et 1.0.

    On compte seulement les lettres.
    Les chiffres, les espaces et la ponctuation ne comptent pas.
    Un texte sans aucune lettre renvoie 0.0.

        "BONJOUR"  ->  1.0
        "bonjour"  ->  0.0
        "Bonjour"  ->  0.143   (1 majuscule sur 7 lettres)

    Indice : pour un caractère c, essayez c.isalpha() et c.isupper().
    """
    # TODO


def regle_majuscules(texte, seuil=0.40, longueur_min=20):
    """
    TODO. Donne POINTS_MAJUSCULES points si le texte a trop de majuscules.

    Il faut les deux conditions à la fois :

    - le ratio de majuscules dépasse `seuil`
    - le texte a au moins `longueur_min` lettres

    LE PIÈGE : "URGENT: RE: TP3" est tout en majuscules.
    Pourtant, c'est un courriel normal.
    Sur 10 lettres, un pourcentage ne veut rien dire.

    Moins de `longueur_min` lettres ? Renvoyez (0, "").

    Indice : ratio_majuscules(texte) donne le ratio.
    """
    # TODO
