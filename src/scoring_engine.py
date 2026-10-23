"""Le moteur qui décide.

Les deux modules produisent chacun un score. Ce fichier tranche.

Il contient aussi les règles déjà écrites et l'assemblage des deux modules :
les règles des élèves (homework/) y sont appelées à côté des règles fournies.
"""

import random
import re

from homework import phishing_rules as ph
from homework import spam_rules as sp
from homework import thresholds
from src import evaluation
from src.email import (
    extraire_domaine_adresse,
    extraire_domaine_url,
    extraire_urls,
    marque_annoncee,
    normaliser,
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


def ancienne_passerelle(courriels, graine=2025):
    """Le code de démonstration resté après l'incident : un verdict au hasard."""
    rng = random.Random(graine)
    return [rng.choice(evaluation.VERDICTS) for _ in courriels]


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


def _ajouter(resultats, couple):
    """Ajoute (points, explication) au bilan, en ignorant les None."""
    if not couple:
        return
    points, explication = couple
    if points:
        resultats.append((points, explication))


def analyser_phishing(courriel, table_marques):
    """
    Applique toutes les règles du module 1 à un courriel.

    `courriel` est un dictionnaire avec les clés :
        sender, name, subject, message, return_path, reply_to

    Renvoie (score_brut, [(points, explication), ...]).
    """
    officiels = tous_les_domaines(table_marques)
    marques = list(table_marques.keys())
    details = []

    domaine_exp = extraire_domaine_adresse(courriel.get("sender", "")) or ""

    # Composante 1.1 — le domaine de l'expéditeur
    if domaine_exp and not ph.domaine_est_officiel(domaine_exp, officiels):
        _ajouter(details, regle_mot_appat(domaine_exp))
        _ajouter(details, regle_extension_risque(domaine_exp))
        _ajouter(details, ph.regle_substitution(domaine_exp, marques))

    # Composante 1.2 — les liens du message
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    marque = marque_annoncee(courriel, marques)
    for url in extraire_urls(texte):
        _ajouter(details, ph.regle_lien_incoherent(url, marque, table_marques))
        _ajouter(details, regle_lien_adresse_ip(url))
        _ajouter(details, regle_lien_raccourcisseur(url))
        _ajouter(details, regle_lien_sans_https(url))

    # Composante 1.3 — nom affiché vs adresse
    _ajouter(
        details,
        ph.regle_nom_vs_adresse(
            courriel.get("name", ""), courriel.get("sender", ""), table_marques
        ),
    )

    # Composante 1.4 — en-têtes
    _ajouter(
        details,
        ph.regle_return_path(
            courriel.get("sender", ""), courriel.get("return_path", "")
        ),
    )
    _ajouter(
        details,
        regle_reply_to(courriel.get("sender", ""), courriel.get("reply_to", "")),
    )

    return sum(p for p, _ in details), details


def analyser_spam(courriel):
    """
    Applique toutes les règles du module 2 à un courriel.
    Renvoie (score_brut, [(points, explication), ...]).
    """
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    details = []

    _ajouter(details, sp.regle_mots_commerciaux(texte))
    _ajouter(details, sp.regle_majuscules(texte))
    _ajouter(details, regle_formulation_promo(texte))
    _ajouter(details, regle_exclamations(texte))
    _ajouter(details, regle_nombre_liens(texte))

    return sum(p for p, _ in details), details


# ==========================================================================
#  DÉCISION
# ==========================================================================

SCORE_MAX = 100

ACTIONS = {
    "phishing": "Blocage + alerte analyste",
    "spam": "Dossier indesirables",
    "suspect": "Mise en quarantaine, revue humaine",
    "ham": "Livraison normale",
}


class ModuleIncomplet(RuntimeError):
    pass


def borner(score):
    """
    Ramène un score brut dans l'intervalle 0–100.

    La somme brute des règles dépasse 100 (module 1 : jusqu'à 130).
    Le plafonnement est implémenté ici. Ce n'est pas un choix neutre.
    """
    return min(max(int(score), 0), SCORE_MAX)


def niveau_de_risque(score_max):
    """Niveau affiché à l'analyste, pour prioriser sa file d'attente."""
    if score_max >= 75:
        return "Critique"
    if score_max >= 50:
        return "Eleve"
    if score_max >= 25:
        return "Moyen"
    return "Faible"


def decider(score_phishing, score_spam):
    """
    Renvoie le verdict : "phishing", "spam", "suspect" ou "ham".

    RÈGLE D'ARBITRAGE — quand les deux scores sont élevés, l'hameçonnage
    l'emporte. Les conséquences ne sont pas comparables : une publicité
    livrée par erreur agace, un vol d'identifiants compromet
    l'organisation. C'est pourquoi on teste le phishing EN PREMIER.
    """
    if score_phishing >= thresholds.SEUIL_PHISHING:
        return "phishing"
    if score_phishing >= thresholds.SEUIL_PHISHING_SUSPECT:
        return "suspect"
    if score_spam >= thresholds.SEUIL_SPAM:
        return "spam"
    if score_spam >= thresholds.SEUIL_SPAM_SUSPECT:
        return "suspect"
    return "ham"


def analyser_courriel(courriel, table_marques):
    """
    Chaîne complète pour un courriel :

    1. analyse hameçonnage (module 1) et spam (module 2) ;
    2. bornage des deux scores bruts ;
    3. décision, niveau de risque et action.

    Si une fonction n'est pas encore écrite, elle renvoie None et l'analyse
    échoue : le message invite alors à lancer la vérification.
    """
    try:
        brut_p, details_p = analyser_phishing(courriel, table_marques)
        brut_s, details_s = analyser_spam(courriel)
        score_p = borner(brut_p)
        score_s = borner(brut_s)
        verdict = decider(score_p, score_s)
    except (TypeError, ValueError, AttributeError) as err:
        raise ModuleIncomplet(
            "Une fonction renvoie None : elle n'est pas encore ecrite. "
            "Lancez la section Verification pour voir lesquelles."
        ) from err

    return {
        "courriel": courriel,
        "score_phishing": score_p,
        "score_spam": score_s,
        "details_phishing": details_p,
        "details_spam": details_s,
        "verdict": verdict,
        "niveau": niveau_de_risque(max(score_p, score_s)),
        "action": ACTIONS[verdict],
    }


def analyser_tous(courriels, table_marques):
    return [analyser_courriel(c, table_marques) for c in courriels]


def afficher_rapport(resultat):
    """Rapport lisible pour un courriel, façon console d'analyste."""
    c = resultat["courriel"]
    print("=" * 58)
    print("  SecuMail 2.0")
    print("=" * 58)
    print(f"Expediteur : {c.get('name', '')} <{c.get('sender', '')}>")
    print(f"Sujet      : {c.get('subject', '')}")

    print("\n--- Analyse hameconnage ---")
    for points, explication in resultat["details_phishing"]:
        print(f"  +{points:<3} {explication}")
    if not resultat["details_phishing"]:
        print("  (aucun indice)")
    print(f"  Score : {resultat['score_phishing']}/100")

    print("\n--- Analyse spam ---")
    for points, explication in resultat["details_spam"]:
        print(f"  +{points:<3} {explication}")
    if not resultat["details_spam"]:
        print("  (aucun indice)")
    print(f"  Score : {resultat['score_spam']}/100")

    print("\n--- Decision ---")
    print(f"  Verdict          : {resultat['verdict'].upper()}")
    print(f"  Niveau de risque : {resultat['niveau']}")
    print(f"  Action           : {resultat['action']}")
    print("=" * 58)
