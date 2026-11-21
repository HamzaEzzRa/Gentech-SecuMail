"""Chargement des données, découpage et remise."""

import csv
import random
from pathlib import Path

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
    domaines_des_marques = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            marque = ligne["marque"].strip().lower()
            domaines = [
                d.strip().lower()
                for d in ligne["domaines_officiels"].split(",")
                if d.strip()
            ]
            domaines_des_marques[marque] = domaines
    return domaines_des_marques


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


def ecrire_predictions(courriels, regles, ml, chemin="predictions.csv"):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "regles", "ml"])
        for courriel, verdict, prediction in zip(courriels, regles, ml):
            writer.writerow([courriel["id"], verdict, prediction])
    return chemin
