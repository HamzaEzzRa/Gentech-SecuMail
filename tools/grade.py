"""Score team predictions on the hidden test set (teachers only).

    python tools/grade.py submissions/*.csv

Each file is a team's predictions.csv (columns id, regles, ml). The team name
is the file name. Needs data/emails_test_labels.csv, which is never published.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import evaluation

LABELS = Path(__file__).resolve().parent.parent / "data" / "emails_test_labels.csv"


def lire(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("remises", nargs="+", type=Path)
    parser.add_argument("--labels", type=Path, default=LABELS)
    args = parser.parse_args()

    cle = {ligne["id"]: ligne["label"] for ligne in lire(args.labels)}
    lignes = []
    for remise in args.remises:
        predictions = {ligne["id"]: ligne for ligne in lire(remise)}
        manquants = set(cle) - set(predictions)
        if manquants:
            print(f"{remise.name} : {len(manquants)} courriels sans prédiction")
        ids = [i for i in cle if i in predictions]
        reels = [cle[i] for i in ids]
        for systeme in ("regles", "ml"):
            verdicts = [predictions[i][systeme] for i in ids]
            lignes.append(
                evaluation.mesures(reels, verdicts, f"{remise.stem} / {systeme}")
            )

    lignes.sort(key=lambda ligne: ligne["cout"])
    evaluation.comparer(*lignes)


if __name__ == "__main__":
    main()
