"""Chargement des données, découpage, réglage et remise, pour main.ipynb."""

import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt

from homework import thresholds
from src import evaluation, scoring_engine

DONNEES = Path(__file__).resolve().parent.parent / "data"
CHEMIN_DONNEES = DONNEES / "emails_train.csv"
CHEMIN_TEST = DONNEES / "emails_test.csv"
CHEMIN_MARQUES = DONNEES / "official_domains.csv"


def charger_courriels(chemin=CHEMIN_DONNEES):
    """Lit le CSV et renvoie une liste de dictionnaires."""
    with open(chemin, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def charger_domaines_officiels(chemin=CHEMIN_MARQUES):
    """
    Lit official_domains.csv et renvoie un dictionnaire :

        {"amazon": ["amazon.ca", "amazon.com"], "netflix": ["netflix.com"], ...}
    """
    table = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            marque = ligne["marque"].strip().lower()
            domaines = [
                d.strip().lower()
                for d in ligne["domaines_officiels"].split(",")
                if d.strip()
            ]
            table[marque] = domaines
    return table


def separer_validation(courriels, part_validation=0.3, graine=42):
    """Same split for every team: 70 % to learn and tune, 30 % to measure."""
    par_classe = {}
    for courriel in courriels:
        par_classe.setdefault(courriel["label"], []).append(courriel)

    rng = random.Random(graine)
    entrainement, validation = [], []

    for classe in sorted(par_classe):
        groupe = list(par_classe[classe])
        rng.shuffle(groupe)
        n_validation = round(len(groupe) * part_validation)
        if len(groupe) > 1:
            n_validation = max(1, n_validation)
        n_validation = min(n_validation, len(groupe))
        validation.extend(groupe[:n_validation])
        entrainement.extend(groupe[n_validation:])

    rng.shuffle(entrainement)
    rng.shuffle(validation)
    return entrainement, validation


def cout_selon_seuil(resultats, reels, nom, valeurs=range(0, 101, 5)):
    """Total cost for each value of one threshold constant, the others unchanged."""
    actuel = getattr(thresholds, nom)
    couts = []
    try:
        for valeur in valeurs:
            setattr(thresholds, nom, valeur)
            verdicts = [
                scoring_engine.decider(r["score_phishing"], r["score_spam"])
                for r in resultats
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


def ecrire_predictions(courriels, regles, ml, chemin="predictions.csv"):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "regles", "ml"])
        for courriel, verdict, prediction in zip(courriels, regles, ml):
            writer.writerow([courriel["id"], verdict, prediction])
    return chemin
