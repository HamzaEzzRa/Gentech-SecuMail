"""Vérifie session4/bayes.py."""

from session4 import bayes as nb
from src.checks import bilan, essai, section


def _courriel(label, subject, message=""):
    """Courriel minimal pour les tests du module 3."""
    return {
        "label": label,
        "name": "",
        "sender": "",
        "return_path": "",
        "reply_to": "",
        "subject": subject,
        "message": message,
    }


def verifier():
    with bilan("MODULE 3, LE MODULE QUI APPREND"):
        jouet = [
            _courriel("spam", "Gagnez un iPhone gratuit, cliquez ici !"),
            _courriel("spam", "Cadeau gratuit pour vous : profitez-en vite."),
            _courriel("spam", "Votre essai gratuit expire demain, cliquez ici."),
            _courriel("spam", "Votre cadeau vous attend, cliquez maintenant."),
            _courriel("spam", "Offre limitée : soldes sur tout le magasin."),
            _courriel("ham", "La réunion de demain est reportée à 14 h."),
            _courriel("ham", "Rappel : réunion du club demain midi."),
            _courriel("ham", "Votre facture est disponible dans votre espace client."),
            _courriel("ham", "Les photos de la réunion sont en ligne, cliquez ici."),
            _courriel(
                "ham", "Votre sortie de demain est confirmée, apportez un lunch."
            ),
        ]
        table_jouet = {
            "gratuit": {"spam": 3, "ham": 0},
            "cliquez": {"spam": 3, "ham": 1},
            "votre": {"spam": 2, "ham": 2},
            "demain": {"spam": 1, "ham": 3},
            "reunion": {"spam": 0, "ham": 3},
        }
        totaux_jouet = {"spam": 5, "ham": 5}

        def appris(choix):
            resultat = nb.apprendre(jouet)
            if resultat is None:
                return None
            return choix(*resultat)

        def classer(texte):
            return nb.classer(_courriel("ham", texte), table_jouet, totaux_jouet)

        section("Module 3 - apprendre (exercice 5.1)")
        essai(
            "« gratuit » est dans 3 spams",
            lambda: appris(lambda t, _: t.get("gratuit", {}).get("spam", 0)),
            3,
        )
        essai(
            "« reunion » est dans 0 spam",
            lambda: appris(lambda t, _: t.get("reunion", {}).get("spam", 0)),
            0,
        )
        essai("5 spams au total", lambda: appris(lambda _, n: n.get("spam")), 5)

        section("Module 3 - points_du_mot")
        essai(
            "« gratuit » vaut +2",
            lambda: nb.points_du_mot("gratuit", "spam", table_jouet, totaux_jouet),
            2.0,
        )
        essai(
            "« reunion » vaut -2",
            lambda: nb.points_du_mot("reunion", "spam", table_jouet, totaux_jouet),
            -2.0,
        )
        essai(
            "un mot absent vaut 0",
            lambda: nb.points_du_mot("inconnu", "spam", table_jouet, totaux_jouet),
            0.0,
        )

        section("Module 3 - classer (exercice 5.2)")
        essai(
            "courriel A -> spam",
            lambda: classer("Cliquez ici : votre cadeau gratuit vous attend !"),
            "spam",
        )
        essai(
            "courriel B -> ham",
            lambda: classer("Réunion demain : cliquez ici pour voir l'horaire."),
            "ham",
        )
        essai(
            "courriel C -> spam (l'erreur de l'exercice 5.4)",
            lambda: classer("Cliquez ici pour voir vos notes du cours."),
            "spam",
        )
