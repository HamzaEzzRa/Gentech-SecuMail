"""Module 1 : qui a vraiment écrit le courriel ?

Les règles déjà écrites, et l'assemblage des règles du module 1 :
vos règles (session2/phishing_rules.py) y sont appelées à côté des règles fournies.
"""

import re

from session2 import phishing_rules as ph
from src.email import (
    extraire_domaine_adresse,
    extraire_domaine_url,
    extraire_urls,
    marque_annoncee,
    tous_les_domaines,
)

# ==========================================================================
#  RESSOURCES  (fournies)
# ==========================================================================

MOTS_APPAT = [
    "security",
    "securite",
    "login",
    "verify",
    "verification",
    "account",
    "compte",
    "update",
    "billing",
    "suivi",
    "remboursement",
    "support",
    "alert",
    "secure",
    "signin",
]

EXTENSIONS_RISQUE = [".xyz", ".tk", ".top", ".info", ".gq", ".ml", ".cf"]

RACCOURCISSEURS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd"]

# ==========================================================================
#  MODULE 1 — RÈGLES DÉJÀ ÉCRITES
# ==========================================================================


def regle_mot_appat(domaine):
    """
    +25 si le domaine contient un mot de MOTS_APPAT.

    Ces mots rassurent la victime (« security », « verify ») et n'ont
    aucune raison d'apparaître dans le domaine d'une vraie marque :
    Amazon écrit depuis amazon.ca, pas depuis amazon-security-login.com.
    """
    if not domaine:
        return 0, ""

    d = str(domaine).lower()
    trouves = []
    for mot in MOTS_APPAT:
        if mot in d:
            trouves.append(mot)

    if trouves:
        mots = ", ".join(trouves)
        explication = "Domaine avec un mot piege : " + mots
        return ph.POINTS_MOT_APPAT, explication

    return 0, ""


def regle_extension_risque(domaine):
    """
    +10 si le domaine se termine par une extension de EXTENSIONS_RISQUE.

    Ces extensions sont gratuites ou quasi gratuites : elles coûtent zéro
    à l'attaquant, qui en jette une après chaque campagne.
    """
    if not domaine:
        return 0, ""

    d = str(domaine).lower().rstrip(".")
    for extension in EXTENSIONS_RISQUE:
        if d.endswith(extension):
            return ph.POINTS_EXTENSION_RISQUE, f"Extension a risque « {extension} »"
    return 0, ""


def regle_lien_adresse_ip(url):
    """
    +25 si le domaine du lien est une adresse IP.

    Une vraie organisation possède un nom de domaine. Une adresse IP sans nom
    signale une machine compromise ou un hébergement jetable — et elle
    empêche la victime de reconnaître un nom familier.
    """
    domaine = extraire_domaine_url(url)
    if domaine and re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domaine):
        return (
            ph.POINTS_LIEN_ADRESSE_IP,
            f"Lien vers une adresse IP au lieu d'un nom : {domaine}",
        )
    return 0, ""


def regle_lien_raccourcisseur(url):
    """
    +15 si le domaine figure dans RACCOURCISSEURS.

    Un raccourcisseur cache la destination réelle : impossible de juger
    le lien avant de cliquer. Ce n'est pas une preuve de fraude — les
    infolettres légitimes en utilisent — d'où un score modéré.
    """
    domaine = extraire_domaine_url(url)
    if not domaine:
        return 0, ""

    domaine = domaine.removeprefix("www.")

    if domaine in RACCOURCISSEURS:
        return (
            ph.POINTS_LIEN_RACCOURCISSEUR,
            f"Lien raccourci ({domaine}) : on ne voit pas ou il mene",
        )
    return 0, ""


def regle_lien_sans_https(url):
    """
    +10 si l'URL ne commence pas par "https://".

    Signal faible en 2026 : le chiffrement est devenu la norme, et un
    site d'hameçonnage peut très bien avoir un certificat. Score modéré
    en conséquence.
    """
    if not url:
        return 0, ""

    if not str(url).strip().lower().startswith("https://"):
        return (
            ph.POINTS_LIEN_SANS_HTTPS,
            "Lien non chiffre (http:// au lieu de https://)",
        )
    return 0, ""


def regle_reply_to(entete_from, entete_reply_to):
    """
    +15 si Reply-To est présent ET si son domaine diffère de celui de From.
    Si Reply-To est vide : (0, "").

    Le détournement classique : le courriel semble venir du fournisseur,
    mais votre réponse — avec le virement modifié — part chez l'attaquant.
    """
    if not entete_reply_to or not str(entete_reply_to).strip():
        return 0, ""

    domaine_from = extraire_domaine_adresse(entete_from)
    domaine_reponse = extraire_domaine_adresse(entete_reply_to)

    if not domaine_from or not domaine_reponse:
        return 0, ""

    if domaine_from != domaine_reponse:
        return ph.POINTS_REPLY_TO, (
            f"Reply-To trompeur : les reponses partiraient vers "
            f"« {domaine_reponse} » et non « {domaine_from} »"
        )
    return 0, ""


# ==========================================================================
#  ASSEMBLAGE  (fourni — ne pas modifier)
# ==========================================================================


def analyser_phishing(courriel, table_marques):
    """
    Applique toutes les règles du module 1 à un courriel.

    `courriel` est un dictionnaire avec les clés :
        sender, name, subject, message, return_path, reply_to

    Renvoie (score_brut, [(points, explication), ...]).
    """
    officiels = tous_les_domaines(table_marques)
    marques = list(table_marques.keys())
    expediteur = courriel.get("sender", "")
    domaine_exp = extraire_domaine_adresse(expediteur) or ""
    couples = []

    # Composante 1.1 — le domaine de l'expéditeur
    if domaine_exp and not ph.domaine_est_officiel(domaine_exp, officiels):
        couples += [
            regle_mot_appat(domaine_exp),
            regle_extension_risque(domaine_exp),
            ph.regle_substitution(domaine_exp, marques),
        ]

    # Composante 1.2 — les liens du message
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    marque = marque_annoncee(courriel, marques)
    for url in extraire_urls(texte):
        couples += [
            ph.regle_lien_incoherent(url, marque, table_marques),
            regle_lien_adresse_ip(url),
            regle_lien_raccourcisseur(url),
            regle_lien_sans_https(url),
        ]

    # Composantes 1.3 et 1.4 — nom affiché et en-têtes
    couples += [
        ph.regle_nom_vs_adresse(courriel.get("name", ""), expediteur, table_marques),
        ph.regle_return_path(expediteur, courriel.get("return_path", "")),
        regle_reply_to(expediteur, courriel.get("reply_to", "")),
    ]

    # une règle pas encore écrite renvoie None
    details = [c for c in couples if c and c[0]]
    return sum(p for p, _ in details), details


def afficher_analyse(courriel, table_marques):
    """Les indices du module 1 pour un courriel, avec leurs points."""
    score, details = analyser_phishing(courriel, table_marques)
    print(f"Expediteur : {courriel.get('name', '')} <{courriel.get('sender', '')}>")
    print(f"Sujet      : {courriel.get('subject', '')}")
    for points, explication in details:
        print(f"  +{points:<3} {explication}")
    if not details:
        print("  (aucun indice)")
    print(f"  Score hameconnage : {score}")
