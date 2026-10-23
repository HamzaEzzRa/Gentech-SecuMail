"""Training, prediction, and explanations for module 3.

Each function tolerates a homework/bayes.py that is not finished yet, so that
main.ipynb runs from the first session.
"""

from homework import bayes
from src.email import mots_du_courriel
from src.evaluation import CLASSES

NOMS = {"ham": "courriels légitimes", "spam": "spams", "phishing": "hameçonnages"}


def entrainer(courriels):
    resultat = bayes.apprendre(courriels)
    if not resultat or len(resultat) != 2:
        return {}, {}
    table, totaux = resultat
    return table or {}, totaux or {}


def _points(mot, categorie, table, totaux):
    points = bayes.points_du_mot(mot, categorie, table, totaux)
    return 0.0 if points is None else float(points)


def predire(courriel, table, totaux):
    if not table:
        return "ham"
    categorie = bayes.classer(courriel, table, totaux)
    return categorie if categorie in CLASSES else "ham"


def predire_tous(courriels, table, totaux):
    return [predire(c, table, totaux) for c in courriels]


def expliquer(courriel, categorie, table, totaux, n=3):
    """The n words that weighed most for the category."""
    poids = sorted(
        ((_points(m, categorie, table, totaux), m) for m in mots_du_courriel(courriel)),
        reverse=True,
    )
    return [
        (
            points,
            f"'{mot}' : {2**points:.0f} fois plus fréquent dans les {NOMS[categorie]}",
        )
        for points, mot in poids[:n]
    ]


def afficher_prediction(courriel, table, totaux):
    categorie = predire(courriel, table, totaux)
    print(f"Module 3 : {categorie.upper()}")
    if table:
        for points, explication in expliquer(courriel, categorie, table, totaux):
            print(f"  {points:+.1f}  {explication}")


def mots_les_plus_forts(table, totaux, categorie, n=10):
    scores = [(_points(mot, categorie, table, totaux), mot) for mot in table]
    scores.sort(reverse=True)
    return [(mot, points) for points, mot in scores[:n]]
