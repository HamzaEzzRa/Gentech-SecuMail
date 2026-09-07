"""
phishing_rules.py — MODULE 1 : détection d'hameçonnage.

Question centrale : l'identité affichée correspond-elle à l'expéditeur réel ?

Ce fichier couvre les composantes 1.1 à 1.4 du guide étudiant.

CONTRAT IMPOSÉ : chaque règle renvoie un couple (points, explication).
Un système de sécurité qui affirme sans justifier est inutilisable en SOC.

Pour vérifier votre avancement :  python3 verification.py
"""

import csv
import re

# ==========================================================================
#  RESSOURCES  (fournies)
# ==========================================================================

MOTS_APPAT = [
    "security", "securite", "login", "verify", "verification",
    "account", "compte", "update", "billing", "suivi",
    "remboursement", "support", "alert", "secure", "signin",
]

EXTENSIONS_RISQUE = [".xyz", ".tk", ".top", ".info", ".gq", ".ml", ".cf"]

SUBSTITUTIONS = {"0": "o", "1": "l", "3": "e", "5": "s", "rn": "m", "vv": "w"}

RACCOURCISSEURS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd"]

MOTIF_URL = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)


def charger_domaines_officiels(chemin="domaines_officiels.csv"):
    """
    FOURNI. Lit domaines_officiels.csv et renvoie un dictionnaire :

        {"amazon": ["amazon.ca", "amazon.com"], "netflix": ["netflix.com"], ...}
    """
    table = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            marque = ligne["marque"].strip().lower()
            domaines = [d.strip().lower()
                        for d in ligne["domaines_officiels"].split(",")
                        if d.strip()]
            table[marque] = domaines
    return table


def tous_les_domaines(table):
    """FOURNI. Liste à plat de tous les domaines officiels connus."""
    return [d for domaines in table.values() for d in domaines]


def extraire_urls(texte):
    """FOURNI. Liste des URL présentes dans un texte."""
    return MOTIF_URL.findall(texte or "")


# ==========================================================================
#  COMPOSANTE 1.1 — CLASSIFICATION DES DOMAINES
# ==========================================================================

def extraire_domaine_adresse(adresse):
    """
    Domaine d'une adresse courriel, en minuscules.

        "Amazon Support <support123@gmail.com>"  ->  "gmail.com"
        "support123@gmail.com"                   ->  "gmail.com"
        ""                                       ->  ""

    Démarche : couper au "@", garder la partie de droite, retirer un ">" final.
    """
    if not adresse:
        return ""

    texte = str(adresse).strip()
    if "@" not in texte:
        return ""

    domaine = texte.split("@")[-1]          # tout ce qui suit le dernier @
    domaine = domaine.strip().strip("<>").strip()
    return domaine.lower()


def extraire_domaine_url(url):
    """
    Domaine d'une URL, en minuscules.

        "https://www.amazon.ca/gp/orders"           ->  "www.amazon.ca"
        "http://amazon.ca.security-check.xyz/login" ->  "amazon.ca.security-check.xyz"

    Démarche : retirer "http://" ou "https://", couper au premier "/",
    puis retirer un éventuel ":port".
    """
    if not url:
        return ""

    reste = str(url).strip()
    for prefixe in ("https://", "http://"):
        if reste.lower().startswith(prefixe):
            reste = reste[len(prefixe):]
            break

    reste = reste.split("/")[0]             # on jette le chemin
    reste = reste.split("?")[0]             # ... et les parametres
    reste = reste.split("#")[0]             # ... et l'ancre
    if "@" in reste:                        # http://user:pass@site.com
        reste = reste.split("@")[-1]
    reste = reste.split(":")[0]             # ... et le :port
    return reste.strip().lower()


def domaine_est_officiel(domaine, domaines_officiels):
    """
    True si `domaine` est un domaine officiel OU un sous-domaine d'un
    domaine officiel.

        "accesd.desjardins.com"               ->  True
        "desjardins.com.securite-client.xyz"  ->  False   <-- LE PIÈGE

    ATTENTION : on compare la FIN du domaine, jamais son contenu.
    Un test `if "desjardins.com" in domaine` classerait le second comme
    légitime — c'est exactement l'erreur que l'attaquant provoque.
    """
    if not domaine or not domaines_officiels:
        return False

    domaine = str(domaine).strip().lower().rstrip(".")
    for officiel in domaines_officiels:
        officiel = str(officiel).strip().lower()
        if not officiel:
            continue
        if domaine == officiel or domaine.endswith("." + officiel):
            return True
    return False


def regle_mot_appat(domaine):
    """
    +25 si le domaine contient un mot de MOTS_APPAT.

    Ces mots rassurent la victime (« security », « verify ») et n'ont
    aucune raison d'apparaître dans le domaine d'une vraie marque :
    Amazon écrit depuis amazon.ca, pas depuis amazon-security-login.com.
    """
    if not domaine:
        return 0, ""

    d = str(domaine).lower()
    trouves = []
    for mot in MOTS_APPAT:
        if mot in d:
            trouves.append(mot)

    if trouves:
        mots = ", ".join(trouves)
        explication = "Domaine contenant un mot d'appat : " + mots
        return 25, explication

    return 0, ""


def regle_extension_risque(domaine):
    """
    +10 si le domaine se termine par une extension de EXTENSIONS_RISQUE.

    Ces extensions sont gratuites ou quasi gratuites : elles coûtent zéro
    à l'attaquant, qui en jette une après chaque campagne.
    """
    if not domaine:
        return 0, ""

    d = str(domaine).lower().rstrip(".")
    for extension in EXTENSIONS_RISQUE:
        if d.endswith(extension):
            return 10, f"Extension a risque « {extension} »"
    return 0, ""


def regle_substitution(domaine, marques_connues):

    if not domaine or not marques_connues:
        return 0, ""

    original = str(domaine).lower()
    corrige = original

    # Remplacer les faux caractères par les vrais
    for faux, vrai in SUBSTITUTIONS.items():
        corrige = corrige.replace(faux, vrai)

    # Si le domaine n'a pas changé
    if corrige == original:
        return 0, ""

    # Vérifier chaque marque
    for marque in marques_connues:

        marque = str(marque).lower()

        if marque in corrige and marque not in original:
            return 30, (f"Substitution de caracteres : « {original} » "
                        f"imite « {marque} » (lu : « {corrige} »)")
    return 0, ""


# ==========================================================================
#  COMPOSANTE 1.2 — ANALYSE DES LIENS
# ==========================================================================

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

    texte = texte.lower()

    for marque in marques_connues:

        marque = str(marque).lower()

        if marque:
            motif = r"\b" + re.escape(marque) + r"\b"

            if re.search(motif, texte):
                return marque

    return None


def regle_lien_incoherent(url, marque, table_marques):
    """
    +25 si le courriel se réclame d'une marque (`marque` non None) ALORS
    QUE le lien pointe ailleurs que vers un domaine officiel de cette marque.

    Si `marque` vaut None : (0, "") — la règle ne s'applique pas.

    POURQUOI CETTE CONDITION EST OBLIGATOIRE
    Une version naïve dirait : « +25 pour tout lien vers un domaine non
    officiel ». Mais la quasi-totalité des liens du monde pointent vers
    des domaines absents de votre liste blanche : le site d'un
    fournisseur, un article de presse, une boutique locale. Cette
    règle-là signalerait presque TOUS les courriels, y compris les
    légitimes — et un détecteur qui crie tout le temps ne détecte rien.

    L'hameçonnage n'est pas « un lien inconnu ». C'est un lien inconnu
    QUI SE FAIT PASSER POUR une marque connue. C'est la contradiction
    qui est l'indice, pas le lien lui-même.
    """
    if not marque or not url:
        return 0, ""

    domaines_marque = table_marques.get(str(marque).lower(), [])

    if not domaines_marque:
        return 0, ""

    domaine = extraire_domaine_url(url)

    if not domaine:
        return 0, ""

    if domaine_est_officiel(domaine, domaines_marque):
        return 0, ""

    explication = "Le courriel se réclame de " + marque
    explication += " mais le lien pointe vers " + domaine

    return 25, explication


def regle_lien_adresse_ip(url):
    """
    +25 si le domaine du lien est une adresse IP.

    Une vraie organisation possède un nom de domaine. Une adresse IP nue
    signale une machine compromise ou un hébergement jetable — et elle
    empêche la victime de reconnaître un nom familier.
    """
    domaine = extraire_domaine_url(url)
    if domaine and re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domaine):
        return 25, f"Lien vers une adresse IP nue : {domaine}"
    return 0, ""


def regle_lien_raccourcisseur(url):
    """
    +15 si le domaine figure dans RACCOURCISSEURS.

    Un raccourcisseur cache la destination réelle : impossible de juger
    le lien avant de cliquer. Ce n'est pas une preuve de fraude — les
    infolettres légitimes en utilisent — d'où un score modéré.
    """
    domaine = extraire_domaine_url(url)
    if not domaine:
        return 0, ""

    if domaine.startswith("www."):
        domaine = domaine[4:]

    if domaine in RACCOURCISSEURS:
        return 15, f"Lien raccourci ({domaine}) : destination masquee"
    return 0, ""


def regle_lien_sans_https(url):
    """
    +10 si l'URL ne commence pas par "https://".

    Signal faible en 2026 : le chiffrement est devenu la norme, et un
    site d'hameçonnage peut très bien avoir un certificat. Score modéré
    en conséquence.
    """
    if not url:
        return 0, ""

    if not str(url).strip().lower().startswith("https://"):
        return 10, "Lien non chiffre (http:// au lieu de https://)"
    return 0, ""


# ==========================================================================
#  COMPOSANTE 1.3 — NOM AFFICHÉ vs ADRESSE D'ENVOI
# ==========================================================================

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

    nom = str(nom_affiche).lower()
    for marque in marques_connues:
        marque = str(marque).lower()
        if marque and re.search(r"\b" + re.escape(marque) + r"\b", nom):
            return marque
    return None


def regle_nom_vs_adresse(nom_affiche, adresse, table_marques):
    """
    +20 si le nom affiché évoque une marque connue ALORS QUE le domaine
    de l'adresse n'est pas un domaine officiel de CETTE marque.

    Le raisonnement se fait en deux temps :
        1. une marque est-elle citée dans le nom affiche ?
           si non -> (0, "") et on ne signale rien
        2. si oui -> le domaine de l'adresse est-il officiel POUR ELLE ?

    Une règle qui se déclenche sur tous les courriels ne discrimine rien :
    « Marie Tremblay <marie@cegep-exemple.qc.ca> » doit rester muet.
    """
    if not table_marques:
        table_marques = {}

    marque = marque_dans_nom(nom_affiche, list(table_marques.keys()))

    if marque is None:
        return 0, ""

    domaine = extraire_domaine_adresse(adresse)

    if not domaine:
        return 0, ""

    domaines_marque = table_marques.get(marque, [])

    if domaine_est_officiel(domaine, domaines_marque):
        return 0, ""

    explication = "Le nom affiche annonce " + marque
    explication += " mais l'adresse provient de " + domaine

    return 20, explication


# ==========================================================================
#  COMPOSANTE 1.4 — EN-TÊTES TECHNIQUES
# ==========================================================================

def regle_return_path(entete_from, entete_return_path):
    """
    +15 si le domaine de From diffère de celui de Return-Path.

    Si Return-Path est vide ou absent : (0, "").
    Une donnée manquante n'est pas une preuve de fraude.

    PIÈGE : "info@infolettre-cuisine.com" et
    "bounce-4471@infolettre-cuisine.com" ont le MÊME domaine.
    C'est le fonctionnement normal d'une infolettre : les rebonds partent
    vers une boîte technique. On compare les DOMAINES, jamais les
    adresses complètes.
    """
    if not entete_return_path or not str(entete_return_path).strip():
        return 0, ""

    domaine_from = extraire_domaine_adresse(entete_from)
    domaine_retour = extraire_domaine_adresse(entete_return_path)

    if not domaine_from or not domaine_retour:
        return 0, ""

    if domaine_from != domaine_retour:
        return 15, (f"Return-Path divergent : envoi reel depuis "
                    f"« {domaine_retour} » et non « {domaine_from} »")
    return 0, ""


def regle_reply_to(entete_from, entete_reply_to):
    """
    +15 si Reply-To est présent ET si son domaine diffère de celui de From.
    Si Reply-To est vide : (0, "").

    Le détournement classique : le courriel semble venir du fournisseur,
    mais votre réponse — avec le virement modifié — part chez l'attaquant.
    """
    if not entete_reply_to or not str(entete_reply_to).strip():
        return 0, ""

    domaine_from = extraire_domaine_adresse(entete_from)
    domaine_reponse = extraire_domaine_adresse(entete_reply_to)

    if not domaine_from or not domaine_reponse:
        return 0, ""

    if domaine_from != domaine_reponse:
        return 15, (f"Reply-To detourne : les reponses partiraient vers "
                    f"« {domaine_reponse} » et non « {domaine_from} »")
    return 0, ""


# ==========================================================================
#  ASSEMBLAGE  (fourni — ne pas modifier)
# ==========================================================================

def _ajouter(resultats, couple):
    """Ajoute (points, explication) au bilan, en ignorant les None."""
    if not couple:
        return
    points, explication = couple
    if points:
        resultats.append((points, explication))


def analyser_phishing(courriel, table_marques):
    """
    FOURNI. Applique toutes les règles du module 1 à un courriel.

    `courriel` est un dictionnaire avec les clés :
        sender, name, subject, message, return_path, reply_to

    Renvoie (score_brut, [(points, explication), ...]).
    """
    officiels = tous_les_domaines(table_marques)
    marques = list(table_marques.keys())
    details = []

    domaine_exp = extraire_domaine_adresse(courriel.get("sender", "")) or ""

    # Composante 1.1 — le domaine de l'expéditeur
    if domaine_exp and not domaine_est_officiel(domaine_exp, officiels):
        _ajouter(details, regle_mot_appat(domaine_exp))
        _ajouter(details, regle_extension_risque(domaine_exp))
        _ajouter(details, regle_substitution(domaine_exp, marques))

    # Composante 1.2 — les liens du message
    texte = f"{courriel.get('subject', '')} {courriel.get('message', '')}"
    marque = marque_annoncee(courriel, marques)
    for url in extraire_urls(texte):
        _ajouter(details, regle_lien_incoherent(url, marque, table_marques))
        _ajouter(details, regle_lien_adresse_ip(url))
        _ajouter(details, regle_lien_raccourcisseur(url))
        _ajouter(details, regle_lien_sans_https(url))

    # Composante 1.3 — nom affiché vs adresse
    _ajouter(details, regle_nom_vs_adresse(
        courriel.get("name", ""), courriel.get("sender", ""), table_marques))

    # Composante 1.4 — en-têtes
    _ajouter(details, regle_return_path(
        courriel.get("sender", ""), courriel.get("return_path", "")))
    _ajouter(details, regle_reply_to(
        courriel.get("sender", ""), courriel.get("reply_to", "")))

    return sum(p for p, _ in details), details