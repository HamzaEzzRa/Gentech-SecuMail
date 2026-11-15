"""Première cellule de chaque notebook : %run ../src/startup.py"""

import sys
from pathlib import Path

from IPython import get_ipython

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
get_ipython().run_line_magic("load_ext", "autoreload")
get_ipython().run_line_magic("autoreload", "2")

from src import evaluation, pipeline  # noqa: F401, the notebook uses both

table_marques = pipeline.charger_domaines_officiels()
courriels = pipeline.charger_courriels()
entrainement, validation = pipeline.separer_validation(courriels)
reels = [c["label"] for c in validation]
