"""Compile the workshop notebooks into reveal.js slides (teachers only).

    uv run python tools/build_slides.py

Writes one HTML file per deck to build/slides/. Each deck is executed first,
from its own folder like in class, so its demos show live results.
"""

import argparse
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "build" / "slides"

# Session, deck. Order follows the course plan.
DECKS = [
    (2, "workshop/phishing/rules.ipynb"),
    (3, "workshop/spam/rules.ipynb"),
    (4, "workshop/ml/naive_bayes.ipynb"),
    (5, "workshop/scoring/engine.ipynb"),
]


def compiler(seance, deck, sortie):
    chemin = Path(deck)
    nom = f"seance{seance}-{chemin.parent.name}-{chemin.stem}"
    commande = [
        sys.executable,
        "-m",
        "nbconvert",
        "--to",
        "slides",
        "--execute",
        "--SlidesExporter.reveal_scroll=True",
        "--SlidesExporter.reveal_number=c/t",
        "--SlidesExporter.embed_images=True",  # images/ travels inside the HTML
        "--output-dir",
        str(sortie),
        "--output",
        nom,
        str(RACINE / deck),
    ]
    subprocess.run(commande, check=True, capture_output=True)
    return sortie / f"{nom}.slides.html"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sortie", type=Path, default=SORTIE)
    args = parser.parse_args()

    args.sortie.mkdir(parents=True, exist_ok=True)
    for seance, deck in DECKS:
        print(compiler(seance, deck, args.sortie).relative_to(RACINE))


if __name__ == "__main__":
    main()
