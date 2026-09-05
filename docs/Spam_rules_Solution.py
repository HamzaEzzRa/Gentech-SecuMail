
import re
import unicodedata

from phishing_rules import extraire_urls


# ==========================================================================
#  OUTIL COMMUN — NORMALISATION
# ==========================================================================

def normaliser(texte):
    """
    Met le texte en minuscules et retire les accents.

    POURQUOI : les courriels de classe sont francophones et écrits
    tantôt « limitée », tantôt « limitee », tantôt « LIMITÉE ».
    Sans cette étape, il faudrait écrire chaque mot-clé en quatre
    versions. On normalise une fois, on compare ensuite.

        "Offre LIMITÉE"  ->  "offre limitee"
    """
    if not texte:
        return ""
    decompose = unicodedata.normalize("NFD", str(texte))
    sans_accent = "".join(c for c in decompose
                          if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", sans_accent).lower()


# ==========================================================================
#  COMPOSANTE 2.1 — MOTS-CLÉS COMMERCIAUX
# ==========================================================================
#
#  Liste bilingue : les corpus réels (SpamAssassin, Enron) sont
#  majoritairement anglophones, les courriels de classe francophones.
#  Une liste unilingue échoue sur la moitié des données.
#
#  Les termes sont écrits SANS ACCENT : le texte analysé passe par
#  normaliser() avant la comparaison.

MOTS_COMMERCIAUX = [
    # --- gratuité / appât ---
    "free", "gratuit", "gratuite", "gratuitement", "cadeau", "bonus",
    # --- gain / loterie ---
    "win", "winner", "gagnez", "gagnant", "prize", "tirage", "loterie",
    "jackpot", "felicitations", "congratulations",
    # --- offre / promotion ---
    "offer", "offre", "promo", "promotion", "deal", "aubaine",
    "exclusive", "exclusif", "exclusivite",
    # --- prix / réduction ---
    "discount", "rabais", "reduction", "solde", "soldes", "liquidation",
    "remise", "coupon", "economisez", "save",
    # --- injonction commerciale ---
    "achetez", "commandez", "buy", "order", "shop", "abonnez",
    "souscrivez", "inscrivez",
    # --- argent ---
    "cash", "argent", "revenu", "income", "investissement", "credit",
    "million", "millionnaire",
    # --- logistique commerciale ---
    "livraison", "shipping", "stock", "stocks",
    # --- mécanique du pourriel ---
    "desabonner", "unsubscribe", "viagra", "casino", "pharmacie",
]


def regle_mots_commerciaux(texte, points_par_mot=3, plafond=15):
    """
    +3 par mot DISTINCT de MOTS_COMMERCIAUX trouvé dans le texte,
    plafonné à 15 points au total.

    Un mot présent trois fois ne compte qu'UNE fois : sinon un seul mot
    répété suffirait à faire exploser le score.

    La comparaison ignore la casse ET les accents, et se fait sur des
    mots entiers (\\b) : sans cela « offre » se déclencherait sur
    « offrez-lui », et « stock » sur « stockholm ».

    Renvoie (points, explication).
    """
    texte_normalise = normaliser(texte)
    if not texte_normalise:
        return 0, ""

    trouves = []
    for mot in MOTS_COMMERCIAUX:
        mot_normalise = normaliser(mot)
        if not mot_normalise:
            continue
        motif = r"\b" + re.escape(mot_normalise) + r"\b"
        if re.search(motif, texte_normalise):
            if mot_normalise not in trouves:      # distinct : une seule fois
                trouves.append(mot_normalise)

    if not trouves:
        return 0, ""

    points = min(len(trouves) * points_par_mot, plafond)
    explication = (f"{len(trouves)} mot(s) commercial(aux) : "
                   f"{', '.join(sorted(trouves))}")
    if len(trouves) * points_par_mot > plafond:
        explication += f" (plafonne a {plafond})"
    return points, explication


# ==========================================================================
#  COMPOSANTE 2.2 — EXCÈS DE MAJUSCULES
# ==========================================================================

def ratio_majuscules(texte):
    """
    Proportion de lettres MAJUSCULES parmi les lettres, entre 0.0 et 1.0.
    Les chiffres, espaces et ponctuation sont ignorés.
    Un texte sans aucune lettre renvoie 0.0.

        "BONJOUR" -> 1.0      "bonjour" -> 0.0      "Bonjour" -> 0.143
    """
    if not texte:
        return 0.0

    lettres = [c for c in str(texte) if c.isalpha()]
    if not lettres:
        return 0.0

    majuscules = sum(1 for c in lettres if c.isupper())
    return majuscules / len(lettres)


def regle_majuscules(texte, seuil=0.40, longueur_min=20):
    """
    +10 si le ratio dépasse `seuil` ET si le texte compte au moins
    `longueur_min` lettres.

    LE PIÈGE : "URGENT: RE: TP3" a un ratio de 1,00 et est parfaitement
    légitime. Sur 10 lettres, une proportion ne veut rien dire — c'est
    la loi des petits nombres. En dessous de longueur_min, on renvoie
    (0, "") sans rien conclure.
    """
    if not texte:
        return 0, ""

    nb_lettres = sum(1 for c in str(texte) if c.isalpha())
    if nb_lettres < longueur_min:
        return 0, ""                      # trop court : aucune conclusion

    ratio = ratio_majuscules(texte)
    if ratio > seuil:
        return 10, (f"Exces de majuscules : {ratio:.0%} des {nb_lettres} "
                    f"lettres (seuil {seuil:.0%})")
    return 0, ""


# ==========================================================================
#  COMPOSANTE 2.3 — FORMULATION PROMOTIONNELLE
# ==========================================================================
#
#  Un MOTIF est plus précis qu'un mot-clé : il exige que plusieurs
#  éléments apparaissent ensemble, dans un certain ordre.
#
#    « croissance de 12 % des ventes »  -> pourcentage seul      -> rien
#    « -50 % de rabais »                -> pourcentage + rabais  -> +10
#
#  Les motifs sont écrits sans accent : le texte est normalisé avant
#  d'être confronté à MOTIF_PROMO.

MOTIFS_PROMO = [
    # pourcentage ACCOMPAGNÉ d'un mot de réduction
    r"-?\s?\d{1,3}\s?%\s?(de\s+)?(rabais|off|reduction|remise|moins)\b",
    r"jusqu'?a\s+-?\s?\d{1,3}\s?%",
    r"(economisez|save)\s+(jusqu'?a\s+|up\s+to\s+)?-?\s?\d",

    # injonction d'achat
    r"achetez\s+(des\s+)?(maintenant|aujourd'?hui|vite)",
    r"buy\s+now",
    r"(commandez|profitez|reservez|inscrivez-vous|cliquez)\s+"
    r"(en\s+|y\s+|des\s+)?(maintenant|aujourd'?hui|vite|ici|sans\s+tarder)",
    r"(order|shop|click|act|subscribe)\s+now",

    # rareté artificielle
    r"offre\s+(limitee|exclusive|speciale|du\s+jour|a\s+ne\s+pas\s+manquer)",
    r"(stocks?|places?|quantites?|temps)\s+limitees?",
    r"limited\s+(time|offer|stock|quantity)",
    r"derni(er|ere)s?\s+(chance|jours?|heures?|minutes?)",
    r"ne\s+manquez\s+pas\s+(cette|notre|ce)",
    r"(se\s+termine|expire)\s+(ce\s+soir|aujourd'?hui|demain|dans\s+\d)",

    # gratuité mise en avant
    r"(100\s?%|totalement|entierement)\s+gratuit",
    r"free\s+(gift|trial|shipping|offer|access|sample)",
    r"livraison\s+gratuite",
    r"essai\s+gratuit",

    # gain annoncé
    r"vous\s+avez\s+(gagne|ete\s+selectionne)",
    r"(gagnez|gagner)\s+(un|une|des|jusqu)",
    r"you\s+(have\s+)?won\b",

    # argument de prix
    r"(prix|tarif)s?\s+(imbattables?|casses?|reduits?|exceptionnels?)",
    r"meilleur\s+prix",
    r"(vente|solde)s?\s+(flash|privee?s?|de\s+liquidation)",
    r"liquidation\s+(totale|complete|finale)",
    r"satisfait\s+ou\s+rembourse",
    r"argent\s+facile",
]

MOTIF_PROMO = re.compile("|".join(MOTIFS_PROMO), re.IGNORECASE)


def regle_formulation_promo(texte):
    """
    +10 si au moins un motif de MOTIFS_PROMO est reconnu.

    Renvoie (points, explication) où l'explication cite le passage trouvé.
    """
    texte_normalise = normaliser(texte)
    if not texte_normalise:
        return 0, ""

    trouve = MOTIF_PROMO.search(texte_normalise)
    if trouve:
        passage = trouve.group().strip()
        return 10, f"Formulation promotionnelle : « {passage} »"
    return 0, ""


# ==========================================================================
#  COMPOSANTE 2.4 — SIGNAUX COMPLÉMENTAIRES
# ==========================================================================

def regle_exclamations(texte, seuil=3):
    """+5 si le texte contient au moins `seuil` points d'exclamation."""
    if not texte:
        return 0, ""

    nombre = str(texte).count("!")
    if nombre >= seuil:
        return 5, f"Ponctuation excessive : {nombre} points d'exclamation"
    return 0, ""


def regle_nombre_liens(texte, seuil=3):
    """
    +10 si le texte contient au moins `seuil` liens.
    Réutilise extraire_urls() importée depuis phishing_rules : une seule
    définition de « qu'est-ce qu'une URL » pour tout le projet.
    """
    if not texte:
        return 0, ""

    urls = extraire_urls(texte)
    if len(urls) >= seuil:
        return 10, f"Message truffe de liens : {len(urls)} URL detectees"
    return 0, ""


# ==========================================================================
#  ASSEMBLAGE  (fourni — ne pas modifier)
# ==========================================================================

def _ajouter(resultats, couple):
    if not couple:
        return
    points, explication = couple
    if points:
        resultats.append((points, explication))


def analyser_spam(courriel):
    """
    FOURNI. Applique toutes les règles du module 2 à un courriel.
    Renvoie (score_brut, [(points, explication), ...]).
    """
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    details = []

    _ajouter(details, regle_mots_commerciaux(texte))
    _ajouter(details, regle_majuscules(texte))
    _ajouter(details, regle_formulation_promo(texte))
    _ajouter(details, regle_exclamations(texte))
    _ajouter(details, regle_nombre_liens(texte))

    return sum(p for p, _ in details), details