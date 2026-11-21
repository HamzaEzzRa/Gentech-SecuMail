"""Vérifie session3/spam_rules.py."""

from session3 import spam_rules as sp
from src.checks import bilan, essai, points, section


def verifier():
    with bilan("MODULE 2, CONTENU DU MESSAGE"):
        section("Composante 2.1 - mots-cles commerciaux")
        essai(
            "un mot repete ne compte qu'une fois",
            lambda: points(sp.regle_mots_commerciaux("gratuit GRATUIT Gratuit")),
            sp.POINTS_MOT_COMMERCIAL,
        )
        essai(
            "aucun mot commercial",
            lambda: points(
                sp.regle_mots_commerciaux("La reunion de lundi est deplacee a 14 h")
            ),
            0,
        )
        essai(
            "plafond respecte",
            lambda: (
                points(sp.regle_mots_commerciaux(" ".join(sp.MOTS_COMMERCIAUX)))
                <= sp.POINTS_MOTS_COMMERCIAUX_MAX
            ),
            True,
        )

        section("Composante 2.2 - trop de majuscules")
        essai("tout en majuscules", lambda: sp.ratio_majuscules("BONJOUR"), 1.0)
        essai("tout en minuscules", lambda: sp.ratio_majuscules("bonjour"), 0.0)
        essai("aucune lettre", lambda: sp.ratio_majuscules("123 !!!"), 0.0)
        essai(
            "texte long, tout en majuscules",
            lambda: points(
                sp.regle_majuscules("FELICITATIONS VOUS AVEZ GAGNE UN IPHONE GRATUIT")
            ),
            sp.POINTS_MAJUSCULES,
        )
        essai(
            "texte long et normal",
            lambda: points(
                sp.regle_majuscules(
                    "Votre facture PDF est disponible dans votre Espace client BMO."
                )
            ),
            0,
        )
        essai(
            "PIEGE : 'URGENT: RE: TP3' est trop court -> 0",
            lambda: points(sp.regle_majuscules("URGENT: RE: TP3")),
            0,
        )
        essai(
            "PIEGE : 'ATTENTION' est trop court -> 0",
            lambda: points(sp.regle_majuscules("ATTENTION")),
            0,
        )
