"""Vérifie vos fonctions : OK, ... ou X.

| Affichage | Sens                                                       |
| --------- | ---------------------------------------------------------- |
| OK        | la fonction renvoie la valeur attendue                     |
| ...       | la fonction n'est pas encore écrite (elle renvoie None)    |
| X         | la fonction répond, mais pas ce qu'il faut, ou elle plante |
"""

from homework import bayes as nb
from homework import phishing_rules as ph
from homework import spam_rules as sp
from src import pipeline
from src.email import tous_les_domaines

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


def _courriel(label, subject, message=""):
    """Courriel minimal pour les tests du module 3."""
    return {
        "label": label,
        "name": "",
        "sender": "",
        "return_path": "",
        "reply_to": "",
        "subject": subject,
        "message": message,
    }


def verifier_module_1():
    table = pipeline.charger_domaines_officiels()
    officiels = tous_les_domaines(table)
    marques = list(table.keys())

    section("Composante 1.1 - le piege du sous-domaine (n° 6 vs n° 7)")
    essai(
        "accesd.desjardins.com est officiel",
        lambda: ph.domaine_est_officiel("accesd.desjardins.com", officiels),
        True,
    )
    essai(
        "desjardins.com.securite-client.xyz ne l'est PAS",
        lambda: ph.domaine_est_officiel(
            "desjardins.com.securite-client.xyz", officiels
        ),
        False,
    )
    essai(
        "amazon.ca est officiel",
        lambda: ph.domaine_est_officiel("amazon.ca", officiels),
        True,
    )
    essai(
        "micr0soft.com ne l'est pas",
        lambda: ph.domaine_est_officiel("micr0soft.com", officiels),
        False,
    )

    section("Composante 1.1 - lettres remplacees")
    essai(
        "substitution 0 pour o",
        lambda: points(ph.regle_substitution("amaz0n.com", marques)),
        ph.POINTS_SUBSTITUTION,
    )
    essai(
        "substitution rn pour m",
        lambda: points(ph.regle_substitution("rnicrosoft.com", marques)),
        ph.POINTS_SUBSTITUTION,
    )
    essai(
        "substitution 1 pour l",
        lambda: points(ph.regle_substitution("paypa1.com", marques)),
        ph.POINTS_SUBSTITUTION,
    )
    essai(
        "domaine sain, aucune substitution",
        lambda: points(ph.regle_substitution("amazon.ca", marques)),
        0,
    )

    section("Composante 1.2 - analyse des liens")
    essai(
        "marque annoncee + lien officiel -> 0",
        lambda: points(
            ph.regle_lien_incoherent("https://www.netflix.com/browse", "netflix", table)
        ),
        0,
    )
    essai(
        "marque annoncee + sous-domaine officiel -> 0",
        lambda: points(
            ph.regle_lien_incoherent(
                "https://accesd.desjardins.com/identification", "desjardins", table
            )
        ),
        0,
    )
    essai(
        "marque annoncee + lien piege -> des points",
        lambda: points(
            ph.regle_lien_incoherent(
                "http://netflix-billing.tk/update.php", "netflix", table
            )
        ),
        ph.POINTS_LIEN_INCOHERENT,
    )
    essai(
        "PIEGE : aucune marque annoncee -> la regle reste MUETTE",
        lambda: points(ph.regle_lien_incoherent("http://bit.ly/aff9921", None, table)),
        0,
    )

    section("Composante 1.3 - nom affiche vs adresse d'envoi")
    essai(
        "usurpation Amazon via gmail",
        lambda: points(
            ph.regle_nom_vs_adresse("Amazon Support", "support123@gmail.com", table)
        ),
        ph.POINTS_NOM_VS_ADRESSE,
    )
    essai(
        "Desjardins depuis son vrai domaine",
        lambda: points(
            ph.regle_nom_vs_adresse(
                "AccesD Desjardins", "noreply@desjardins.com", table
            )
        ),
        0,
    )
    essai(
        "Microsoft depuis microsoftonline.com",
        lambda: points(
            ph.regle_nom_vs_adresse(
                "Equipe Microsoft 365", "no-reply@microsoftonline.com", table
            )
        ),
        0,
    )
    essai(
        "nom de personne : la regle reste MUETTE",
        lambda: points(
            ph.regle_nom_vs_adresse(
                "Marie Tremblay", "marie@cegep-exemple.qc.ca", table
            )
        ),
        0,
    )

    section("Composante 1.4 - en-tetes techniques")
    essai(
        "Return-Path identique",
        lambda: points(
            ph.regle_return_path(
                "marie@cegep-exemple.qc.ca", "marie@cegep-exemple.qc.ca"
            )
        ),
        0,
    )
    essai(
        "Return-Path different",
        lambda: points(
            ph.regle_return_path(
                "securite@desjardins.com", "x9921@relais-etranger.info"
            )
        ),
        ph.POINTS_RETURN_PATH,
    )
    essai(
        "infolettre : adresse differente, MEME domaine",
        lambda: points(
            ph.regle_return_path(
                "info@infolettre-cuisine.com", "bounce-4471@infolettre-cuisine.com"
            )
        ),
        0,
    )
    essai(
        "Return-Path absent : ne rien conclure",
        lambda: points(ph.regle_return_path("rh@entreprise-exemple.qc.ca", "")),
        0,
    )


def verifier_module_2():
    section("Composante 2.1 - mots-cles commerciaux")
    essai("liste d'au moins 20 termes", lambda: len(sp.MOTS_COMMERCIAUX) >= 20, True)
    essai(
        "liste bilingue (au moins un mot accentue ou francais)",
        lambda: any(
            m in sp.MOTS_COMMERCIAUX for m in ["gratuit", "rabais", "gagnez", "offre"]
        ),
        True,
    )
    essai(
        "un mot repete ne compte qu'une fois",
        lambda: points(sp.regle_mots_commerciaux("gratuit GRATUIT Gratuit")),
        sp.POINTS_MOT_COMMERCIAL,
    )
    essai(
        "aucun mot commercial",
        lambda: points(
            sp.regle_mots_commerciaux("La reunion de lundi est deplacee a 14 h")
        ),
        0,
    )
    essai(
        "plafond respecte",
        lambda: (
            points(sp.regle_mots_commerciaux(" ".join(sp.MOTS_COMMERCIAUX)))
            <= sp.POINTS_MOTS_COMMERCIAUX_MAX
        ),
        True,
    )

    section("Composante 2.2 - trop de majuscules")
    essai("tout en majuscules", lambda: sp.ratio_majuscules("BONJOUR"), 1.0)
    essai("tout en minuscules", lambda: sp.ratio_majuscules("bonjour"), 0.0)
    essai("aucune lettre", lambda: sp.ratio_majuscules("123 !!!"), 0.0)
    essai(
        "texte long, tout en majuscules",
        lambda: points(
            sp.regle_majuscules("FELICITATIONS VOUS AVEZ GAGNE UN IPHONE GRATUIT")
        ),
        sp.POINTS_MAJUSCULES,
    )
    essai(
        "texte long et normal",
        lambda: points(
            sp.regle_majuscules(
                "Votre facture PDF est disponible dans votre Espace client BMO."
            )
        ),
        0,
    )
    essai(
        "PIEGE : 'URGENT: RE: TP3' est trop court -> 0",
        lambda: points(sp.regle_majuscules("URGENT: RE: TP3")),
        0,
    )
    essai(
        "PIEGE : 'ATTENTION' est trop court -> 0",
        lambda: points(sp.regle_majuscules("ATTENTION")),
        0,
    )


def verifier_module_3():
    jouet = [
        _courriel("spam", "Gagnez un iPhone gratuit, cliquez ici !"),
        _courriel("spam", "Cadeau gratuit pour vous : profitez-en vite."),
        _courriel("spam", "Votre essai gratuit expire demain, cliquez ici."),
        _courriel("spam", "Votre cadeau vous attend, cliquez maintenant."),
        _courriel("spam", "Offre limitée : soldes sur tout le magasin."),
        _courriel("ham", "La réunion de demain est reportée à 14 h."),
        _courriel("ham", "Rappel : réunion du club demain midi."),
        _courriel("ham", "Votre facture est disponible dans votre espace client."),
        _courriel("ham", "Les photos de la réunion sont en ligne, cliquez ici."),
        _courriel("ham", "Votre sortie de demain est confirmée, apportez un lunch."),
    ]
    table_jouet = {
        "gratuit": {"spam": 3, "ham": 0},
        "cliquez": {"spam": 3, "ham": 1},
        "votre": {"spam": 2, "ham": 2},
        "demain": {"spam": 1, "ham": 3},
        "reunion": {"spam": 0, "ham": 3},
    }
    totaux_jouet = {"spam": 5, "ham": 5}

    def appris(choix):
        resultat = nb.apprendre(jouet)
        if resultat is None:
            return None
        return choix(*resultat)

    def classer(texte):
        return nb.classer(_courriel("ham", texte), table_jouet, totaux_jouet)

    section("Module 3 - apprendre (exercice 5.1)")
    essai(
        "« gratuit » est dans 3 spams",
        lambda: appris(lambda t, _: t.get("gratuit", {}).get("spam", 0)),
        3,
    )
    essai(
        "« reunion » est dans 0 spam",
        lambda: appris(lambda t, _: t.get("reunion", {}).get("spam", 0)),
        0,
    )
    essai("5 spams au total", lambda: appris(lambda _, n: n.get("spam")), 5)

    section("Module 3 - points_du_mot")
    essai(
        "« gratuit » vaut +2",
        lambda: nb.points_du_mot("gratuit", "spam", table_jouet, totaux_jouet),
        2.0,
    )
    essai(
        "« reunion » vaut -2",
        lambda: nb.points_du_mot("reunion", "spam", table_jouet, totaux_jouet),
        -2.0,
    )
    essai(
        "un mot absent vaut 0",
        lambda: nb.points_du_mot("inconnu", "spam", table_jouet, totaux_jouet),
        0.0,
    )

    section("Module 3 - classer (exercice 5.2)")
    essai(
        "courriel A -> spam",
        lambda: classer("Cliquez ici : votre cadeau gratuit vous attend !"),
        "spam",
    )
    essai(
        "courriel B -> ham",
        lambda: classer("Réunion demain : cliquez ici pour voir l'horaire."),
        "ham",
    )
    essai(
        "courriel C -> spam (l'erreur de l'exercice 5.4)",
        lambda: classer("Cliquez ici pour voir vos notes du cours."),
        "spam",
    )


def run():
    """Exécute toute la vérification et affiche le bilan."""
    _stats.update(ok=0, echec=0, attente=0)

    print("=" * 64)
    print("  VERIFICATION DE VOS FONCTIONS")
    print("=" * 64)

    verifier_module_1()
    verifier_module_2()
    verifier_module_3()

    total = _stats["ok"] + _stats["echec"] + _stats["attente"]
    print("=" * 64)
    print(
        f"  BILAN : {_stats['ok']} reussis · {_stats['echec']} echoues · "
        f"{_stats['attente']} a faire   (sur {total})"
    )
    print("=" * 64)
    if _stats["echec"] == 0 and _stats["attente"] == 0:
        print("  Tout est vert. Passez a la mesure dans main.ipynb.")
    elif _stats["attente"]:
        print("  Continuez : completez les fonctions marquees TODO.")
    else:
        print("  Corrigez les X avant de passer a la mesure.")
    print()
    return _stats


if __name__ == "__main__":
    run()
