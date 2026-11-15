"""Check the session notebooks, then compile the slide decks (teachers only).

    uv run python tools/build_slides.py

Writes slides/session<N>/<deck>.ipynb to build/slides/session<N>-<deck>.slides.html.
Each deck is executed first, from its own folder like in class, so its demos
show live results.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import check_sessions

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "build" / "slides"


def compiler(deck, sortie):
    nom = f"{deck.parent.name}-{deck.stem}"
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
        str(deck),
    ]
    subprocess.run(commande, check=True, capture_output=True)
    return sortie / f"{nom}.slides.html"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sortie", type=Path, default=SORTIE)
    args = parser.parse_args()

    check_sessions.main()

    args.sortie.mkdir(parents=True, exist_ok=True)
    for deck in sorted(RACINE.glob("slides/session*/*.ipynb")):
        print(compiler(deck, args.sortie).relative_to(RACINE))


if __name__ == "__main__":
    main()
