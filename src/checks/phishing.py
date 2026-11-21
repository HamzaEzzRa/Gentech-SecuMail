"""Vérifie session2/phishing_rules.py."""

from session2 import phishing_rules as ph
from src import pipeline
from src.checks import bilan, essai, points, section
from src.email import tous_les_domaines


def verifier():
    with bilan("MODULE 1, IDENTITE DE L'EXPEDITEUR"):
        domaines_des_marques = pipeline.charger_domaines_officiels()
        officiels = tous_les_domaines(domaines_des_marques)
        marques = list(domaines_des_marques.keys())

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
                ph.regle_lien_incoherent(
                    "https://www.netflix.com/browse", "netflix", domaines_des_marques
                )
            ),
            0,
        )
        essai(
            "marque annoncee + sous-domaine officiel -> 0",
            lambda: points(
                ph.regle_lien_incoherent(
                    "https://accesd.desjardins.com/identification",
                    "desjardins",
                    domaines_des_marques,
                )
            ),
            0,
        )
        essai(
            "marque annoncee + lien piege -> des points",
            lambda: points(
                ph.regle_lien_incoherent(
                    "http://netflix-billing.tk/update.php",
                    "netflix",
                    domaines_des_marques,
                )
            ),
            ph.POINTS_LIEN_INCOHERENT,
        )
        essai(
            "PIEGE : aucune marque annoncee -> la regle reste MUETTE",
            lambda: points(
                ph.regle_lien_incoherent(
                    "http://bit.ly/aff9921", None, domaines_des_marques
                )
            ),
            0,
        )

        section("Composante 1.3 - nom affiche vs adresse d'envoi")
        essai(
            "usurpation Amazon via gmail",
            lambda: points(
                ph.regle_nom_vs_adresse(
                    "Amazon Support", "support123@gmail.com", domaines_des_marques
                )
            ),
            ph.POINTS_NOM_VS_ADRESSE,
        )
        essai(
            "Desjardins depuis son vrai domaine",
            lambda: points(
                ph.regle_nom_vs_adresse(
                    "AccesD Desjardins", "noreply@desjardins.com", domaines_des_marques
                )
            ),
            0,
        )
        essai(
            "Microsoft depuis microsoftonline.com",
            lambda: points(
                ph.regle_nom_vs_adresse(
                    "Equipe Microsoft 365",
                    "no-reply@microsoftonline.com",
                    domaines_des_marques,
                )
            ),
            0,
        )
        essai(
            "nom de personne : la regle reste MUETTE",
            lambda: points(
                ph.regle_nom_vs_adresse(
                    "Marie Tremblay", "marie@cegep-exemple.qc.ca", domaines_des_marques
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
