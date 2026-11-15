"""Module 2 : le message cherche-t-il à vendre ?

Les règles déjà écrites, et l'assemblage des règles du module 2 :
vos règles (session3/spam_rules.py) y sont appelées à côté des règles fournies.
"""

from session3 import spam_rules as sp
from src.email import extraire_urls, normaliser

# ==========================================================================
#  MODULE 2 — RÈGLES DÉJÀ ÉCRITES
# ==========================================================================


def regle_formulation_promo(texte):
    """
    +10 si au moins une expression de EXPRESSIONS_PROMO est reconnue.

    Renvoie (points, explication) où l'explication cite le passage trouvé.
    """
    texte_normalise = normaliser(texte)
    if not texte_normalise:
        return 0, ""

    for expression in sp.EXPRESSIONS_PROMO:
        if expression in texte_normalise:
            return (
                sp.POINTS_FORMULATION_PROMO,
                f"Expression publicitaire : « {expression} »",
            )
    return 0, ""


def regle_exclamations(texte, seuil=3):
    """+5 si le texte contient au moins `seuil` points d'exclamation."""
    if not texte:
        return 0, ""

    nombre = str(texte).count("!")
    if nombre >= seuil:
        return (
            sp.POINTS_EXCLAMATIONS,
            f"Trop de points d'exclamation : {nombre}",
        )
    return 0, ""


def regle_nombre_liens(texte, seuil=3):
    """
    +10 si le texte contient au moins `seuil` liens.
    Réutilise extraire_urls() : une seule définition de « qu'est-ce
    qu'une URL » pour tout le projet.
    """
    if not texte:
        return 0, ""

    urls = extraire_urls(texte)
    if len(urls) >= seuil:
        return (
            sp.POINTS_NOMBRE_LIENS,
            f"Message plein de liens : {len(urls)} liens trouves",
        )
    return 0, ""


# ==========================================================================
#  ASSEMBLAGE  (fourni — ne pas modifier)
# ==========================================================================


def analyser_spam(courriel):
    """
    Applique toutes les règles du module 2 à un courriel.
    Renvoie (score_brut, [(points, explication), ...]).
    """
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    couples = [
        sp.regle_mots_commerciaux(texte),
        sp.regle_majuscules(texte),
        regle_formulation_promo(texte),
        regle_exclamations(texte),
        regle_nombre_liens(texte),
    ]

    # une règle pas encore écrite renvoie None
    details = [c for c in couples if c and c[0]]
    return sum(p for p, _ in details), details
