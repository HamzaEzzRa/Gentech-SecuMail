"""Outils fournis pour lire un courriel : adresses, liens, marques et mots."""

import re
import unicodedata

MOTIF_URL = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)

# Noms sous lesquels une marque apparaît dans un texte, quand ils diffèrent
# de sa clé dans official_domains.csv.
AUTRES_NOMS = {
    "postescanada": ["postes canada", "canada post"],
    "hydroquebec": ["hydro quebec"],
    "revenuquebec": ["revenu quebec"],
}


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
    sans_accent = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", sans_accent).lower()


def mots_du_texte(texte):
    """
    Liste des mots d'un texte, en minuscules et sans accents.

        "Offre GRATUITE sur concours-gratuit.top !"
        -> ["offre", "gratuite", "sur", "concours", "gratuit", "top"]
    """
    return re.findall(r"[a-z0-9]+", normaliser(texte))


CHAMPS = ["name", "sender", "return_path", "reply_to", "subject", "message"]


def mots_du_courriel(courriel):
    """Ensemble des mots DIFFÉRENTS d'un courriel, tous champs confondus."""
    texte = " ".join(str(courriel.get(champ) or "") for champ in CHAMPS)
    return set(mots_du_texte(texte))


def tous_les_domaines(table):
    """Liste à plat de tous les domaines officiels connus."""
    return [d for domaines in table.values() for d in domaines]


def extraire_urls(texte):
    """Liste des URL présentes dans un texte."""
    return MOTIF_URL.findall(texte or "")


def extraire_domaine_adresse(adresse):
    """
    Domaine d'une adresse courriel, en minuscules.

        "Amazon Support <support123@gmail.com>"  ->  "gmail.com"
        "support123@gmail.com"                   ->  "gmail.com"
        ""                                       ->  ""
    """
    if not adresse:
        return ""

    texte = str(adresse).strip()
    if "@" not in texte:
        return ""

    domaine = texte.split("@")[-1]  # tout ce qui suit le dernier @
    domaine = domaine.strip().strip("<>").strip()
    return domaine.lower()


def extraire_domaine_url(url):
    """
    Domaine d'une URL, en minuscules.

        "https://www.amazon.ca/gp/orders"           ->  "www.amazon.ca"
        "http://amazon.ca.security-check.xyz/login" ->  "amazon.ca.security-check.xyz"
    """
    if not url:
        return ""

    reste = str(url).strip()
    for prefixe in ("https://", "http://"):
        if reste.lower().startswith(prefixe):
            reste = reste[len(prefixe) :]
            break

    reste = reste.split("/")[0]  # on jette le chemin
    reste = reste.split("?")[0]  # ... et les parametres
    reste = reste.split("#")[0]  # ... et l'ancre
    if "@" in reste:  # http://user:pass@site.com
        reste = reste.split("@")[-1]
    reste = reste.split(":")[0]  # ... et le :port
    return reste.strip().lower()


def _cite(marque, texte):
    """True si le texte nomme la marque, sous sa clé ou un de ses AUTRES_NOMS."""
    texte = normaliser(texte).replace("-", " ")
    for nom in [marque, *AUTRES_NOMS.get(marque, [])]:
        if re.search(r"\b" + re.escape(nom) + r"\b", texte):
            return True
    return False


def marque_annoncee(courriel, marques_connues):
    """
    Renvoie la marque que le courriel PRÉTEND représenter, ou None.

    On cherche dans le nom affiché, le sujet et le message.

        name="Netflix", subject="Echec de paiement"     ->  "netflix"
        name="Super Rabais", subject="LIQUIDATION"      ->  None

    Le `\\b` (frontière de mot) évite qu'une marque courte se déclenche
    au milieu d'un autre mot. Pourquoi cette fonction est indispensable :
    voir regle_lien_incoherent().
    """
    if not courriel or not marques_connues:
        return None

    texte = ""
    texte += str(courriel.get("name", "") or "")
    texte += " "
    texte += str(courriel.get("subject", "") or "")
    texte += " "
    texte += str(courriel.get("message", "") or "")

    for marque in marques_connues:
        marque = str(marque).lower()
        if marque and _cite(marque, texte):
            return marque

    return None


def marque_dans_nom(nom_affiche, marques_connues):
    """
    Renvoie le nom de la marque détectée dans le nom affiché, ou None.

        "Amazon Support"  ->  "amazon"
        "Marie Tremblay"  ->  None

    Rappel : le nom affiché est choisi LIBREMENT par l'expéditeur.
    N'importe qui peut s'appeler « Amazon Support ». C'est précisément
    pour cela qu'il faut le confronter à l'adresse réelle.
    """
    if not nom_affiche or not marques_connues:
        return None

    for marque in marques_connues:
        marque = str(marque).lower()
        if marque and _cite(marque, nom_affiche):
            return marque
    return None
