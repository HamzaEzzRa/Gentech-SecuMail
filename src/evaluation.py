"""Mesure de la qualité du système.

L'exactitude (accuracy) est INTERDITE comme mesure principale : si 80 % des
courriels sont légitimes, un système qui répond toujours « ham » obtient
80 % d'exactitude et ne détecte aucune attaque.

Le système peut répondre « suspect » (quarantaine), qui n'est ni une
livraison ni un blocage. Or les étiquettes n'ont que trois valeurs. On
calcule donc les mesures sous DEUX politiques :

    PRUDENTE    suspect -> phishing   la quarantaine compte comme un blocage
    PERMISSIVE  suspect -> ham        la quarantaine compte comme une livraison
"""

import pandas as pd
from sklearn.metrics import classification_report

CLASSES = ["ham", "spam", "phishing"]
VERDICTS = ["ham", "spam", "suspect", "phishing"]

# Coût relatif des erreurs. À lire ainsi : bloquer un courriel légitime
# comme hameçonnage est 10 fois plus grave que laisser passer une pub.
COUTS = {
    ("ham", "spam"): 5,
    ("ham", "suspect"): 3,
    ("ham", "phishing"): 10,
    ("spam", "ham"): 1,
    ("spam", "suspect"): 1,
    ("spam", "phishing"): 2,
    ("phishing", "ham"): 8,
    ("phishing", "suspect"): 2,
    ("phishing", "spam"): 3,
}

POLITIQUES = {
    "prudente": "phishing",  # suspect traité comme une menace
    "permissive": "ham",  # suspect traité comme livrable
}


def matrice_confusion(reels, verdicts):
    """
    Tableau 3 lignes (vraie classe) × 4 colonnes (verdict rendu).

    Le reindex() force l'ordre des lignes et des colonnes et ajoute les cases
    vides : sans lui, une classe jamais prédite disparaîtrait du tableau.
    """
    df = pd.DataFrame({"reel": list(reels), "verdict": list(verdicts)})
    m = pd.crosstab(df["reel"], df["verdict"])
    m = m.reindex(index=CLASSES, columns=VERDICTS, fill_value=0)
    m.index = [f"reel:{c}" for c in CLASSES]
    m.columns = [f"pred:{v}" for v in VERDICTS]
    return m


def cout_total(reels, verdicts):
    """Somme pondérée des erreurs, selon le tableau COUTS. Plus bas = mieux."""
    return sum(COUTS.get((r, v), 0) for r, v in zip(reels, verdicts) if r != v)


def appliquer_politique(verdicts, politique="prudente"):
    """Remplace « suspect » par la classe imposée par la politique."""
    cible = POLITIQUES[politique]
    return [cible if v == "suspect" else v for v in verdicts]


def mesures(reels, verdicts, titre="Resultats"):
    """Les mesures clés de rapport(), sans rien afficher."""
    reels = list(reels)
    verdicts = list(verdicts)

    resultat = {
        "titre": titre,
        "quarantaine": verdicts.count("suspect"),
        "cout": cout_total(reels, verdicts),
        "erreurs": sum(1 for r, v in zip(reels, verdicts) if r != v),
    }
    for politique in POLITIQUES:
        detail = classification_report(
            reels,
            appliquer_politique(verdicts, politique),
            labels=CLASSES,
            output_dict=True,
            zero_division=0,
        )
        resultat[f"f1_macro_{politique}"] = detail["macro avg"]["f1-score"]
        resultat[f"rappel_phishing_{politique}"] = detail["phishing"]["recall"]
        resultat[f"precision_phishing_{politique}"] = detail["phishing"]["precision"]
        resultat[f"rappel_ham_{politique}"] = detail["ham"]["recall"]
    return resultat


def rapport(reels, verdicts, titre="Resultats"):
    """
    Bilan complet. Affiche :

    1. la matrice de confusion des verdicts bruts (avec la colonne suspect) ;
    2. le nombre de courriels mis en quarantaine ;
    3. précision, rappel et F1 par classe, sous les deux politiques ;
    4. le nombre d'erreurs et le coût total pondéré.

    Renvoie le dictionnaire de mesures clés, à passer à comparer().
    """
    reels = list(reels)
    verdicts = list(verdicts)
    resultat = mesures(reels, verdicts, titre)

    print("\n" + "=" * 66)
    print(f"  {titre}")
    print("=" * 66)

    print("\nMatrice de confusion (verdicts bruts)")
    print(matrice_confusion(reels, verdicts).to_string())

    print(f"\nMis en quarantaine : {resultat['quarantaine']} / {len(verdicts)}")

    for politique, cible in POLITIQUES.items():
        print(f"\n--- Politique {politique.upper()} (suspect -> {cible}) ---")
        print(
            classification_report(
                reels,
                appliquer_politique(verdicts, politique),
                labels=CLASSES,
                zero_division=0,
                digits=3,
            )
        )

    print(f"Erreurs (verdicts bruts) : {resultat['erreurs']} / {len(reels)}")
    print(f"Cout total pondere       : {resultat['cout']}  (plus bas = mieux)")

    return resultat


def montrer_erreurs(courriels, reels, verdicts, n=8):
    """
    Affiche les courriels mal classés, la matière première de l'analyse
    d'erreurs. Renvoie la liste complète des fautes, même si elle n'en
    affiche que les n premières.
    """
    fautes = [(c, r, v) for c, r, v in zip(courriels, reels, verdicts) if r != v]
    print(f"\n--- {len(fautes)} erreur(s), {min(n, len(fautes))} affichee(s) ---")
    for c, r, v in fautes[:n]:
        print(f"  reel={r:<9} verdict={v:<9} | {c.get('subject', '')[:48]}")
    return fautes


def comparer(*resultats):
    """
    Tableau comparatif des approches. On lui passe plusieurs dictionnaires
    renvoyés par rapport() : chaque titre devient une ligne du tableau.
    """
    tableau = pd.DataFrame(resultats).set_index("titre")
    print("\n" + "=" * 66)
    print("  COMPARAISON DES APPROCHES")
    print("=" * 66)
    print(tableau.round(3).to_string())
    return tableau
