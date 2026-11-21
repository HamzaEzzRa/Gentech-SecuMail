"""Le moteur qui décide.

Les deux modules produisent chacun un score. Ce fichier tranche,
avec les seuils de session5/thresholds.py.
"""

import matplotlib.pyplot as plt

from session5 import thresholds
from src import evaluation
from src.phishing import analyser_phishing
from src.spam import analyser_spam

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


def analyser_courriel(courriel, domaines_des_marques):
    """
    Chaîne complète pour un courriel :

    1. analyse hameçonnage (module 1) et spam (module 2) ;
    2. bornage des deux scores bruts ;
    3. décision, niveau de risque et action.

    Si une fonction n'est pas encore écrite, elle renvoie None et l'analyse
    échoue : le message invite alors à lancer la vérification.
    """
    try:
        brut_p, details_p = analyser_phishing(courriel, domaines_des_marques)
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


def analyser_tous(courriels, domaines_des_marques):
    return [analyser_courriel(c, domaines_des_marques) for c in courriels]


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


def cout_selon_seuil(resultats, reels, nom, valeurs=range(0, 101, 5)):
    """Total cost for each value of one threshold constant, the others unchanged."""
    actuel = getattr(thresholds, nom)
    couts = []
    try:
        for valeur in valeurs:
            setattr(thresholds, nom, valeur)
            verdicts = [
                decider(r["score_phishing"], r["score_spam"]) for r in resultats
            ]
            couts.append(evaluation.cout_total(reels, verdicts))
    finally:
        setattr(thresholds, nom, actuel)
    return list(valeurs), couts


def tracer_cout_selon_seuil(resultats, reels, nom):
    valeurs, couts = cout_selon_seuil(resultats, reels, nom)
    actuel = getattr(thresholds, nom)
    plt.figure(figsize=(8, 3))
    plt.plot(valeurs, couts, marker="o")
    plt.axvline(actuel, color="gray", linestyle="--", label=f"actuel : {actuel}")
    plt.xlabel(nom)
    plt.ylabel("coût total")
    plt.title(f"Coût des erreurs selon {nom}")
    plt.legend()
    plt.show()
