"""Vérifie vos fonctions : OK, ... ou X.

| Affichage | Sens                                                       |
| --------- | ---------------------------------------------------------- |
| OK        | la fonction renvoie la valeur attendue                     |
| ...       | la fonction n'est pas encore écrite (elle renvoie None)    |
| X         | la fonction répond, mais pas ce qu'il faut, ou elle plante |
"""

from contextlib import contextmanager

_stats = {"ok": 0, "echec": 0, "attente": 0}


def essai(nom, fonction, attendu, tolerance=1e-6):
    """Exécute votre fonction et compare le résultat à la valeur attendue."""
    try:
        obtenu = fonction()
    except Exception as err:  # noqa: BLE001 - on veut voir l'erreur de l'élève
        print(f"  X   {nom} : {type(err).__name__}: {err}")
        _stats["echec"] += 1
        return

    # None est parfois la BONNE reponse (ex. aucune marque detectee).
    # On ne le lit comme « pas encore fait » que si autre chose etait attendu.
    if obtenu is None and attendu is not None:
        print(f"  ...  {nom} : pas encore fait")
        _stats["attente"] += 1
        return

    if isinstance(attendu, float):
        try:
            ok = abs(obtenu - attendu) < tolerance
        except TypeError:
            ok = False
    else:
        ok = obtenu == attendu

    if ok:
        print(f"  OK   {nom}")
        _stats["ok"] += 1
    else:
        print(f"  X    {nom}   (obtenu {obtenu!r}, attendu {attendu!r})")
        _stats["echec"] += 1


def points(couple):
    """Extrait les points d'un couple (points, explication)."""
    return None if couple is None else couple[0]


def section(titre):
    print(f"\n{titre}")
    print("-" * len(titre))


@contextmanager
def bilan(titre):
    """Les essais du bloc, puis le bilan."""
    _stats.update(ok=0, echec=0, attente=0)
    print("=" * 64)
    print(f"  VERIFICATION : {titre}")
    print("=" * 64)

    yield

    total = _stats["ok"] + _stats["echec"] + _stats["attente"]
    print("=" * 64)
    print(
        f"  BILAN : {_stats['ok']} reussis · {_stats['echec']} echoues · "
        f"{_stats['attente']} a faire   (sur {total})"
    )
    print("=" * 64)
    if _stats["echec"] == 0 and _stats["attente"] == 0:
        print("  Tout est vert. Passez a la suite du notebook.")
    elif _stats["attente"]:
        print("  Continuez : completez les fonctions marquees TODO.")
    else:
        print("  Corrigez les X avant de passer a la suite.")
    print()
