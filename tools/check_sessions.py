"""Run each session notebook with only the files students have that day (teachers only).

    uv run python tools/check_sessions.py

Uses the files git tracks, as they are on disk. A file held back for a later
session makes the notebook fail here, not in class.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import nbformat
import yaml
from nbclient import NotebookClient

RACINE = Path(__file__).resolve().parent.parent


def main():
    manifeste = yaml.safe_load((RACINE / "eclorithme.yaml").read_text())
    inclus = manifeste["workspace"]["include"]
    sortie = subprocess.run(
        ["git", "-C", str(RACINE), "ls-files", "--", *inclus],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    fichiers = set(sortie.splitlines())
    seances = manifeste["sessions"]
    debloques = {s["id"]: {*s.get("open", []), *s.get("files", [])} for s in seances}
    libres = fichiers - set().union(*debloques.values())

    # the kernel must import from the copy only
    os.environ.pop("PYTHONPATH", None)
    os.environ["MPLBACKEND"] = "Agg"
    with tempfile.TemporaryDirectory() as dossier:
        for seance in seances:
            espace = Path(dossier) / f"seance{seance['id']}"
            for fichier in libres | debloques[seance["id"]]:
                (espace / fichier).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(RACINE / fichier, espace / fichier)

            notebook = espace / next(p for p in seance["open"] if p.endswith(".ipynb"))
            nb = nbformat.read(notebook, as_version=4)
            client = NotebookClient(
                nb, timeout=300, resources={"metadata": {"path": notebook.parent}}
            )
            client.execute()
            print("OK", notebook.relative_to(espace))


if __name__ == "__main__":
    main()
