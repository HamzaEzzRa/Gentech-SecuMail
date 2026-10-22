"""Labelled email corpus (ham, spam, phishing) as CSV.

    python tools/generate_corpus.py --ham 400 --spam 300 --phishing 300

Template syntax:
    [a|b]   random option per occurrence, nestable
    {slot}  SLOTS value, shared by all fields of an email
"""

import argparse
import csv
import random
import re
import string
import sys
import unicodedata
from collections import Counter
from itertools import zip_longest
from pathlib import Path

DATASETS = Path(__file__).resolve().parent.parent / "datasets"

SCHOOL_DOMAIN = "dessources.qc.ca"


def person(first, last, title=""):
    """title: "M." or "Mme" for staff."""
    local = unicodedata.normalize("NFKD", f"{title.rstrip('.') or first}.{last}")
    return {
        "name": f"{title or first} {last}",
        "first": first,
        "email": f"{local.encode('ascii', 'ignore').decode().lower()}@{SCHOOL_DOMAIN}",
    }


FIRST_NAMES_F = [
    "Émilie",
    "Juliette",
    "Rosalie",
    "Léa",
    "Florence",
    "Camille",
    "Maëlle",
    "Laurence",
    "Béatrice",
    "Sophie",
    "Amélie",
    "Noémie",
    "Charlotte",
    "Zoé",
    "Annabelle",
]
FIRST_NAMES_M = [
    "Simon",
    "Gabriel",
    "Félix",
    "William",
    "Thomas",
    "Nathan",
    "Antoine",
    "Olivier",
    "Charles",
    "Louis",
    "Édouard",
    "Jacob",
    "Raphaël",
    "Émile",
    "Lucas",
]
FIRST_NAMES = FIRST_NAMES_F + FIRST_NAMES_M
LAST_NAMES = [
    "Tremblay",
    "Gagnon",
    "Roy",
    "Côté",
    "Bouchard",
    "Gauthier",
    "Morin",
    "Lavoie",
    "Fortin",
    "Gagné",
    "Ouellet",
    "Pelletier",
    "Bélanger",
    "Lévesque",
    "Bergeron",
    "Leblanc",
    "Girard",
    "Fournier",
    "Caron",
    "Dubois",
    "Boisvert",
]
TEACHERS = [
    person("", last, title)
    for title, last in [
        ("M.", "Bergeron"),
        ("Mme", "Fortin"),
        ("M.", "Gagnon"),
        ("Mme", "Lavoie"),
        ("M.", "Roy"),
        ("Mme", "Bélanger"),
        ("M.", "Caron"),
        ("Mme", "Girard"),
        ("M.", "Pelletier"),
        ("Mme", "Morin"),
    ]
]
# Consonant-initial: no elision in "de {course}"
COURSES = [
    "mathématiques",
    "français",
    "sciences",
    "géographie",
    "musique",
    "chimie",
    "physique",
    "danse",
]
SPORTS = ["hockey", "soccer", "basketball", "volleyball", "badminton"]
MUSEUMS = [
    "Musée des sciences",
    "Biodôme",
    "Planétarium",
    "Musée des beaux-arts",
    "Centre d'histoire",
]
BOOKS = [
    "La forêt mystérieuse",
    "Les ailes de Léa",
    "Le secret du phare",
    "La nuit des étoiles",
    "L'île aux loups",
]
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin"]
DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
TIMES = ["8 h 15", "10 h 30", "12 h", "12 h 15", "13 h", "15 h 30", "16 h"]


def student():
    return person(random.choice(FIRST_NAMES), random.choice(LAST_NAMES))


def reader_greeting(generic):
    """Generic greeting or "Bonjour <prénom>,"."""
    return random.choice([*generic, f"Bonjour {random.choice(FIRST_NAMES)},"])


SLOTS = {
    "school": lambda: SCHOOL_DOMAIN,
    "teacher": lambda: random.choice(TEACHERS),
    "student": student,
    "student_f": lambda: person(
        random.choice(FIRST_NAMES_F), random.choice(LAST_NAMES)
    ),
    "friend": student,
    "course": lambda: random.choice(COURSES),
    "sport": lambda: random.choice(SPORTS),
    "museum": lambda: random.choice(MUSEUMS),
    "book": lambda: random.choice(BOOKS),
    "day": lambda: random.choice(DAYS),
    "month": lambda: random.choice(MONTHS),
    "date": lambda: f"{random.randint(2, 28)} {random.choice(MONTHS)}",
    "time": lambda: random.choice(TIMES),
    "room": lambda: (
        f"{random.choice('ABCD')}-{random.randint(1, 3)}{random.randint(1, 20):02d}"
    ),
    "tp": lambda: f"TP{random.randint(2, 6)}",
    "hello": lambda: reader_greeting(["Bonjour,"]),
    "dear": lambda: reader_greeting(
        ["Bonjour,", "Cher client,", "Chère cliente,", "Avis important :"]
    ),
    "amount": lambda: f"{random.randint(5, 250)},{random.randint(0, 99):02d} $",
    "pct": lambda: random.choice([20, 25, 30, 40, 50, 60, 70, 80]),
    "hours": lambda: random.choice([12, 24, 48, 72]),
    "units": lambda: random.randint(2, 5),
    "n3": lambda: random.randint(100, 999),
    "n4": lambda: random.randint(1000, 9999),
    "order": lambda: f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}",
    "track": lambda: " ".join(str(random.randint(1000, 9999)) for _ in range(4)),
    "code": lambda: "".join(random.choices(string.ascii_letters + string.digits, k=6)),
    "code2": lambda: "".join(random.choices(string.ascii_letters + string.digits, k=6)),
    "ip": lambda: (
        f"{random.choice(['192.0.2', '198.51.100', '203.0.113'])}."
        f"{random.randint(2, 254)}"
    ),
}

ALTERNATIVES = re.compile(
    r"\[([^\[\]]*\|[^\[\]]*)\]"
)  # pipe required: skips {slot[key]}


def render(text, slots):
    count = 1
    while count:  # innermost first
        text, count = ALTERNATIVES.subn(
            lambda m: random.choice(m.group(1).split("|")), text
        )
    return text.format_map(slots)


HEADERS = ["sender", "name", "subject", "message", "return_path", "reply_to"]


def email(*fields):
    """(sender, name, subject, message[, return_path[, reply_to]])"""
    return fields


DIRECTION = "direction@{school}"


def admin(subject, message):
    return email(DIRECTION, "École secondaire", subject, message, DIRECTION)


def teacher(subject, message):
    return email(
        "{teacher[email]}", "{teacher[name]}", subject, message, "{teacher[email]}"
    )


def from_student(subject, message):
    return email("{student[email]}", "{student[name]}", subject, message)


def with_bounce(sender, name, subject, message):
    """Return-Path: bounce address on the sender's domain."""
    return email(sender, name, subject, message, "bounce-{n4}@" + sender.split("@")[1])


HAM = [
    # school administration
    admin(
        "Rappel des devoirs",
        "[Bonjour|Bonjour à tous], petit rappel : les devoirs de {course} doivent "
        "être remis {day}. [Bonne semaine !|Bon travail !|Merci !]\n\n{teacher[name]}",
    ),
    admin(
        "Fermeture hâtive {day}",
        "Avis aux élèves : l'école fermera à [13 h|14 h|15 h] {day} pour [une "
        "réunion des enseignants|une formation du personnel]. Les autobus partiront "
        "[15|20|30] minutes après la fermeture.\n\nLa direction",
    ),
    admin(
        "Livre à retourner",
        "Rappel de la bibliothèque : « {book} » doit être retourné d'ici {day}. "
        "[Merci !|Merci de votre collaboration.]\n\n[Mme Fortin, "
        "bibliothécaire|L'équipe de la bibliothèque]",
    ),
    admin(
        "Pratique de {sport}",
        "Entraînement de {sport} {day} à {time} au gymnase. N'oubliez pas [votre "
        "équipement|vos espadrilles] et votre bouteille d'eau. [On compte sur vous "
        "!|Soyez à l'heure !]\n\n{teacher[name]}",
    ),
    admin(
        "Sortie au {museum}",
        "La sortie au {museum} est confirmée pour le {date}. Veuillez rapporter la "
        "permission signée au secrétariat avant {day}.\n\n{teacher[name]}",
    ),
    admin(
        "Menu de la semaine",
        "Menu de la cafétéria de {day} : [poutine|pâté chinois|spaghetti|soupe aux "
        "légumes], [salade du jardin|crudités|pain de blé] et [compote de "
        "pommes|yogourt|galette à l'avoine]. Bon appétit !\n\nLe service de "
        "cafétéria",
    ),
    admin(
        "Tournoi de {sport}",
        "Le tournoi de {sport} interclasses aura lieu le {date}. Les inscriptions se "
        "font au secrétariat jusqu'à {day}.\n\n{teacher[name]}",
    ),
    admin(
        "Club de [robotique|sciences|photo|théâtre]",
        "Rencontre du club {day} à {time} au local {room}. [Apportez votre "
        "ordinateur portable.|Les nouveaux membres sont bienvenus.|Une collation "
        "sera servie.]\n\n{teacher[name]}",
    ),
    admin(
        "Soirée portes ouvertes",
        "Les parents sont invités à la soirée portes ouvertes le {date} à [18 h|18 h "
        "30|19 h]. [Une garderie sera disponible sur place.|Les enseignants seront "
        "présents dans leurs locaux.]\n\nLa direction",
    ),
    admin(
        "Récupération en {course}",
        "Séance de récupération en {course} : {day} à {time} au local {room}. "
        "Aucune inscription requise.\n\n{teacher[name]}",
    ),
    admin(
        "Répétition de la chorale",
        "Répétition de la chorale {day} à {time} à l'auditorium. Présence "
        "obligatoire pour le spectacle [de fin d'année|du printemps].\n\n{teacher[name]}",
    ),
    admin(
        "Club de bénévolat",
        "Le club de bénévolat cherche des élèves pour [la bibliothèque "
        "municipale|la banque alimentaire|la résidence pour aînés], les {day}s après "
        "l'école. Inscription au local {room}.\n\n{teacher[name]}",
    ),
    admin(
        "Journée thématique",
        "Ce {day}, c'est la journée [pyjama|chapeau fou|rétro|aux couleurs de "
        "l'école] pour le carnaval d'hiver ! Apportez [2|3|5] $ pour la fondation "
        "de l'école.\n\nLe comité étudiant",
    ),
    admin(
        "Publication des bulletins",
        "Les bulletins [de la première étape|de mi-année|de la deuxième étape] "
        "seront disponibles sur le portail des parents {day} après-midi.\n\n[Le "
        "secrétariat|La direction]",
    ),
    admin(
        "Changement d'itinéraire",
        "Petit changement : l'autobus [2|3|5|7|11] partira de la rue [des "
        "Érables|des Pins|Principale|du Couvent] à partir de {day}.\n\nLe transport "
        "scolaire",
    ),
    admin(
        "Trousse d'urgence",
        "[Rappel : la|La] trousse d'urgence de l'école doit être complétée avec "
        "[des gants et une bouteille d'eau|une lampe de poche et des piles|une "
        "couverture et des barres tendres] avant {day}. Merci de votre "
        "collaboration.\n\nLa direction",
    ),
    # friends, family, clubs
    from_student(
        "Hockey [samedi|dimanche] ?",
        "[Salut|Allô] ! Tu viens jouer au hockey dehors ce week-end ? On se rejoint "
        "au parc [des Hirondelles|du Lac|Jarry] à [10 h|13 h|14 h].\n\n"
        "{student[first]}",
    ),
    email(
        "{student_f[email]}",
        "{student_f[name]}",
        "Question sur le devoir",
        "Allô ! Pour le devoir de {course}, je me suis perdue à la question "
        "[2|3|4|5|7]. On se voit à la bibliothèque [demain midi|après "
        "l'école|{day}] ?\n\n{student_f[first]}",
    ),
    email(
        "[mamie.tremblay|grandmaman.roy|lise.gagnon]@[videotron.ca|gmail.com]",
        "Grand-maman",
        "Souper de dimanche",
        "[Bonjour mon trésor|Coucou mon chou|Allô mon grand], tu viens souper dimanche ? Je fais ton [gâteau aux "
        "carottes|pâté chinois|pouding chômeur|macaroni au fromage] préféré "
        "!\n\nGrand-maman",
    ),
    from_student(
        "Partie en ligne {day}",
        "[Salut|Allô] ! Mon cousin m'a prêté un nouveau jeu. On joue en ligne {day} "
        "soir après tes devoirs ?\n\n{student[first]}",
    ),
    from_student(
        "Pour le projet de sciences",
        "Coucou ! Pour le projet de sciences, j'ai trouvé un site avec plein "
        "d'informations sur [les volcans|les planètes|les dinosaures|le corps "
        "humain]. Je te l'envoie [demain|ce soir].\n\n{student[first]}",
    ),
    email(
        "coach.martin@{school}",
        "Coach Martin",
        "Entraînement samedi",
        "Salut ! L'équipe de soccer s'entraîne samedi à [9 h|10 h|13 h] au terrain "
        "du parc. N'oublie pas ton chandail [rouge|bleu|vert][| et ta gourde| et tes protège-tibias].\n\nCoach Martin",
    ),
    from_student(
        "Invitation à ma fête",
        "[Allô|Salut] ! Ma fête de fin de session est [samedi|dimanche|vendredi "
        "soir] à [14 h|15 h|18 h] chez moi. Tu peux [confirmer ta présence|me dire "
        "si tu viens] ?\n\n{student[first]}",
    ),
    from_student(
        "Fournitures pour le projet",
        "Salut ! Peux-tu m'attendre après le cours de {course} ? On doit [passer au "
        "magasin|aller à la papeterie] pour [le projet|l'affiche|la "
        "maquette].\n\n{student[first]}",
    ),
    from_student(
        "Excursion à vélo",
        "Allô ! Si le temps est beau [samedi|dimanche], on fait une excursion à vélo "
        "le long [de la rivière|du canal|du lac]. Tu es de la partie "
        "?\n\n{student[first]}",
    ),
    email(
        "lucie.[bouchard|girard|morin]@videotron.ca",
        "Marraine Lucie",
        "Photos du voyage",
        "Bonjour [mon grand|ma grande|mon cœur], j'ai des photos de notre voyage "
        "[au Saguenay|en Gaspésie|à Québec] à te montrer. Viens me voir [après "
        "l'école|cette fin de semaine|dimanche].\n\nMarraine Lucie",
    ),
    from_student(
        "Liste pour le camping",
        "Salut ! Pour le camping, voici ma liste : tente, sac de couchage, [lampe "
        "de poche|lampe frontale], [barres tendres|guimauves] et "
        "[chasse-moustiques|imperméable]. À [vendredi|samedi] !\n\n{student[first]}",
    ),
    from_student(
        "Cahier oublié",
        "Salut ! As-tu mon cahier de {course} ? Je pense l'avoir oublié au local "
        "{room}. Merci !\n\n{student[first]}",
    ),
    email(
        "sports@{school}",
        "Le comité des sports",
        "Début de saison",
        "Bonjour, la saison de [soccer|baseball|ultimate] commence le {date}. Les "
        "uniformes seront distribués {day}.\n\nLe comité des sports",
    ),
    email(
        "club.lecture@{school}",
        "Le club de lecture",
        "Club de lecture",
        "Chers membres, le club de lecture se réunit {day} à {time}. Nouveau livre "
        ": « {book} ».\n\nLe club de lecture",
    ),
    email(
        "journal@{school}",
        "Le journal étudiant",
        "Journal de l'école",
        "Bonjour, votre abonnement au journal de l'école est [enregistré|confirmé] "
        ": premier numéro {day}. Passez nous voir au local {room} pour toute "
        "question.\n\nLe journal étudiant",
    ),
    from_student(
        "Partie de cartes {day}",
        "Bonjour ! La partie de cartes de {day} est déplacée chez {friend[first]}. "
        "Apporte tes [chips|jus|jeux] préférés !\n\n{student[first]}",
    ),
    # teachers
    teacher(
        "Résultats de l'examen",
        "Bonjour, vos résultats de l'examen de {course} sont corrigés. [Vous avez "
        "bien travaillé, continuez ainsi !|La moyenne du groupe est de [68|72|75|81] "
        "%.|Nous ferons le retour en classe {day}.]\n\n{teacher[name]}",
    ),
    from_student(
        "Question sur le devoir",
        "Bonjour {teacher[name]}, une petite question sur le devoir de {course} : au "
        "numéro [2|3|5|8], on doit souligner les [verbes ou les adjectifs|noms ou "
        "les pronoms] ? Merci !\n\n{student[name]}",
    ),
    teacher(
        "Projet à remettre",
        "Rappel : le projet de sciences est à remettre {day} avant [16 h|midi|la fin "
        "du cours]. N'oubliez pas votre [carnet de laboratoire|rapport "
        "imprimé|affiche].\n\n{teacher[name]}",
    ),
    teacher(
        "Laboratoire de chimie",
        "Avis aux élèves du cours de chimie : portez votre sarrau et vos lunettes "
        "pour la séance de laboratoire de {day}. [Les cheveux longs doivent être "
        "attachés.|Aucune nourriture n'est permise au labo.|À bientôt !]"
        "\n\n{teacher[name]}",
    ),
    teacher(
        "Lecture pour {day}",
        "Lecture à faire pour {day} : le chapitre [2|3|4|5|6] du roman « {book} ». "
        "[Un petit quiz vous attend !|Prenez des notes.]\n\n{teacher[name]}",
    ),
    teacher(
        "Examen de {course} devancé",
        "Changement d'horaire : l'examen de {course} est devancé à {day} [au lieu "
        "de la semaine prochaine|au lieu de vendredi]. Bonne révision !"
        "\n\n{teacher[name]}",
    ),
    teacher(
        "Résultats du quiz",
        "Bonjour, les résultats du quiz de {course} sont affichés sur le portail. "
        "On reprendra le chapitre [1|2|3|4] en classe.\n\n{teacher[name]}",
    ),
    teacher(
        "Atelier optionnel",
        "Atelier optionnel de [programmation|robotique|montage vidéo] : [samedi "
        "matin|{day} midi] au local {room}. Maximum [12|15|20] places.\n\n{teacher[name]}",
    ),
    teacher(
        "Révision avant l'examen",
        "Exercices de révision avant l'examen : pages [12 à 18|18 à 25|30 à "
        "36|40 à 47] du cahier. Les réponses seront corrigées en classe {day}."
        "\n\n{teacher[name]}",
    ),
    teacher(
        "Concours de mathématiques",
        "Le concours de mathématiques [du district|régional] aura lieu le {date}. "
        "Les élèves intéressés doivent me le dire avant {day}.\n\n{teacher[name]}",
    ),
    # real brands, official domains
    email(
        "comptes@hydroquebec.com",
        "Hydro-Québec",
        "Votre facture de {month} est disponible",
        "Votre facture de {month} est accessible dans votre Espace client. Montant "
        ": {amount}. [Aucune action requise si vous êtes inscrit au prélèvement "
        "automatique.|Date d'échéance : le {date}.]\n\nHydro-Québec",
        "comptes@hydroquebec.com",
    ),
    email(
        "noreply@desjardins.com",
        "AccèsD Desjardins",
        "Transaction sur votre compte",
        "{hello} une transaction de {amount} a été effectuée sur votre compte "
        "AccèsD le {date}. Consultez vos relevés sur accesd.desjardins.com pour "
        "les détails.\n\nDesjardins",
        "noreply@desjardins.com",
    ),
    email(
        "noreply@steampowered.com",
        "Steam",
        "Confirmation de votre achat",
        "{hello} votre achat de « [Stardew Valley|Celeste|Terraria|Hollow Knight] "
        "» ({amount}) est confirmé. Le téléchargement du jeu est disponible dans "
        "votre bibliothèque Steam.\n\nL'équipe Steam",
        "noreply@steampowered.com",
    ),
    email(
        "info@netflix.com",
        "Netflix",
        "Votre abonnement est renouvelé",
        "{hello} nous vous confirmons le renouvellement de votre abonnement "
        "Netflix [Essentiel|Standard|Premium] le {date}. Aucune action requise. "
        "Merci !\n\nNetflix",
        "info@netflix.com",
    ),
    email(
        "receipts@apple.com",
        "Apple",
        "Reçu de l'App Store",
        "{hello} voici votre reçu de l'App Store pour l'application [de "
        "mathématiques|de dessin|de langues|de musique]. Montant : {amount}."
        "\n\nApple",
        "receipts@apple.com",
    ),
    email(
        "comptes@bmo.com",
        "BMO",
        "Confirmation de virement",
        "{hello} votre virement de {amount} a été effectué avec succès. Un accusé "
        "[vous a été envoyé par courriel|est disponible dans votre espace client]."
        "\n\nBMO",
        "comptes@bmo.com",
    ),
    email(
        "commande@amazon.ca",
        "Amazon.ca",
        "Votre commande est expédiée",
        "{hello} votre commande est expédiée ! Vous pouvez suivre le colis sur "
        "amazon.ca avec le numéro {track}. Livraison prévue le {date}."
        "\n\nAmazon.ca",
        "commande@amazon.ca",
    ),
    email(
        "noreply@microsoftonline.com",
        "Équipe Microsoft 365",
        "Votre mot de passe expirera bientôt",
        "{hello} votre mot de passe Microsoft expirera dans [7|14|30] jours. "
        "Mettez-le à jour sur outlook.live.com lorsque vous aurez le temps."
        "\n\nMicrosoft",
        "noreply@microsoftonline.com",
    ),
    # newsletter
    with_bounce(
        "info@infolettre-cuisine.com",
        "Infolettre Cuisine",
        "Infolettre - recettes de la semaine",
        "[Voici notre infolettre de la semaine|Au menu cette semaine|Nouvelle infolettre] : [5|6|8] recettes [de saison|pour "
        "la boîte à lunch|végétariennes] avec des légumes du Québec. Pour vous "
        "désabonner, utilisez le lien en bas de page.\n\nL'équipe Cuisine du coin",
    ),
    with_bounce(
        "info@bibliotheque-municipale.qc.ca",
        "La bibliothèque",
        "Nouveautés de la bibliothèque",
        "Nouveautés : [8|10|12|15] nouvelles bandes dessinées et [5|8|10] romans "
        "jeunesse sont arrivés. [Bonne lecture !|Venez les emprunter !|Réservez-les en ligne.]\n\nLa bibliothèque",
    ),
    with_bounce(
        "info@sports-quartier.qc.ca",
        "Le comité des sports",
        "Bulletin des sports du quartier",
        "Le bulletin des sports du quartier : inscriptions au camp de "
        "[soccer|basketball|natation], match de hockey {day} et [résultats|classement] de "
        "la ligue.\n\nLe comité des sports",
    ),
    with_bounce(
        "journal@{school}",
        "Le journal de l'école",
        "Le journal de l'école est arrivé",
        "Le journal de l'école vous salue ! Ce mois-ci : l'entrevue avec [la "
        "gagnante|le gagnant] du concours de [poésie|dessin|sciences] et les photos "
        "de la journée [carnaval|sportive|plein air].\n\nLe comité du journal",
    ),
    with_bounce(
        "info@ecoaction.qc.ca",
        "EcoAction",
        "Infolettre de l'environnement",
        "L'infolettre de l'environnement : le grand ménage de printemps du parc "
        "[des Hirondelles|du Lac|Jarry] est {day}. [Des gants seront fournis.|Apportez vos gants.|Collation offerte.]"
        "\n\nEcoAction",
    ),
    with_bounce(
        "club@echecs-ecole.qc.ca",
        "Le club d'échecs",
        "Tournoi interne {day}",
        "Le club d'échecs publie son infolettre : tournoi interne {day} à {time}, "
        "niveau débutant bienvenu.\n\nLe club d'échecs",
    ),
    with_bounce(
        "coop@{school}",
        "La coop scolaire",
        "Fruits et légumes de la semaine",
        "La coop scolaire a reçu ses fruits et légumes de la semaine : "
        "[pommes|poires|clémentines], [bananes|raisins] et "
        "[carottes|concombres|céleri]. Passez nous voir !\n\nLa coop",
    ),
    # transaction
    with_bounce(
        "info@librairie-du-quartier.ca",
        "Librairie du quartier",
        "Confirmation de votre commande",
        "Bonjour, merci pour votre commande n° {order} ! Elle sera livrée le {date} "
        "entre 9 h et 17 h. Bonne lecture !\n\nLibrairie du quartier",
    ),
    with_bounce(
        "boutique@{school}",
        "La boutique étudiante",
        "Reçu de votre achat",
        "Voici le reçu de votre achat à la boutique du cours d'entrepreneuriat : "
        "[2|3|4] marque-pages et [1 chandail|1 tasse|1 casquette]. Total : "
        "{amount}. Merci de votre soutien !\n\nLa boutique étudiante",
    ),
    with_bounce(
        "inscription@camp-hirondelles.ca",
        "Le camp des Hirondelles",
        "Votre inscription est confirmée",
        "Votre inscription au camp de jour est confirmée pour la semaine du [29 "
        "juin|6 juillet|13 juillet|20 juillet]. Le paiement de {amount} est reçu."
        "\n\nLe camp des Hirondelles",
    ),
    with_bounce(
        "journal@{school}",
        "Le journal étudiant",
        "Abonnement renouvelé",
        "Votre abonnement au journal étudiant est renouvelé jusqu'en "
        "[juin|décembre]. Le premier numéro arrive {day}. [Merci de votre fidélité !|Bonne lecture !|]\n\nLe journal étudiant",
    ),
    with_bounce(
        "secretaire@{school}",
        "Le secrétariat",
        "Réservation de local confirmée",
        "Réservation confirmée : le local {room} est réservé pour votre "
        "présentation de {day} à {time}.\n\nLe secrétariat",
    ),
    # traps: legit emails that trigger rules
    email(
        "info@infolettre-cuisine.com",
        "Infolettre Cuisine",
        "Votre renouvellement",
        "Bonjour, profitez de [15|20|25] % de rabais sur votre renouvellement "
        "d'abonnement à notre infolettre de recettes — vous êtes membre depuis "
        "[2018|2019|2020|2021] ! [Merci de votre fidélité.|Merci d'être avec nous.]\n\nCuisine du coin",
    ),
    email(
        "coop@{school}",
        "La coop scolaire",
        "Rapport trimestriel",
        "Rapport trimestriel de la coop scolaire : croissance de [8|12|15|18] % des "
        "ventes de [pommes|jus|grignotines]. [Merci aux bénévoles !|Bravo à toute l'équipe !]\n\nLa coop",
    ),
    email(
        "secretaire@{school}",
        "Le secrétariat",
        "ATTENTION : changement de local",
        "ATTENTION : changement de local pour le cours de {course} de {day}. Le "
        "nouveau local est le {room}.\n\nLe secrétariat",
    ),
    email(
        "mme.fortin@{school}",
        "Mme Fortin",
        "URGENT : RE: {tp}",
        "URGENT : RE: {tp} — la date limite de remise est reportée au {date}. "
        "Merci !\n\nMme Fortin",
    ),
    email(
        "m.roy@{school}",
        "M. Roy",
        "Victoire au {sport} !",
        "Félicitations à l'équipe gagnante du tournoi de {sport} !!! "
        "[Deux|Trois|Quatre] belles victoires en finale. [On est fiers de vous|Bravo à tous] "
        "!\n\nM. Roy",
    ),
    email(
        "comite@{school}",
        "Le comité étudiant",
        "Concours de l'école",
        "Bonjour, le concours de [poésie|dessin|nouvelles] de l'école offre la "
        "chance de gagner des livres. La remise des prix aura lieu [au gala de fin "
        "d'année|le {date}].\n\nLe comité étudiant",
    ),
    email(
        "m.caron@{school}",
        "M. Caron",
        "Liens pour vos travaux",
        "Voici les liens pour [vos travaux|le projet de {course}] : "
        "https://www.apple.com/ca/fr/support pour le tutoriel, "
        "https://outlook.live.com/mail/ pour votre boîte et "
        "https://www.postescanada.ca/suivi pour suivre votre envoi. [Bonne chance "
        "!|Bon travail !|À {day} !]\n\nM. Caron",
    ),
    email(
        "bibliotheque@{school}",
        "La bibliothèque",
        "Entrée gratuite au musée",
        "GRATUIT pour les membres : l'entrée au {museum} est offerte avec votre "
        "carte de la bibliothèque [cette fin de semaine|le {date}].\n\nLa "
        "bibliothèque",
    ),
    # short
    email(
        "secretaire@{school}",
        "Le secrétariat",
        "ATTENTION",
        "ATTENTION : changement de local pour {day}. [Voir la liste au tableau.|Détails au secrétariat.]"
        "\n\nLe secrétariat",
    ),
    email(
        "mme.fortin@{school}",
        "Mme Fortin",
        "URGENT : RE: {tp}",
        "URGENT : RE: {tp} — reporté au {date}.\n\nMme Fortin",
    ),
    email(
        "m.roy@{school}",
        "M. Roy",
        "RAPPEL",
        "RAPPEL : pratique de {sport} annulée [ce soir|demain].\n\nM. Roy",
    ),
    email(
        "cafeteria@{school}",
        "La cafétéria",
        "INFO",
        "INFO : la cafétéria ferme à [12 h|13 h|14 h] {day}.\n\nLa cafétéria",
    ),
    email(
        DIRECTION,
        "La direction",
        "CHANGEMENT",
        "CHANGEMENT : l'examen de {course} est déplacé à {day}.\n\nLa direction",
    ),
    # links
    email(
        "noreply@desjardins.com",
        "AccèsD Desjardins",
        "Accès à vos relevés",
        "{hello} pour consulter vos relevés [de {month}|du mois], connectez-vous "
        "sur https://accesd.desjardins.com/identification. [Merci !|Bonne journée "
        "!]\n\nDesjardins",
    ),
    email(
        "info@netflix.com",
        "Netflix",
        "Catalogue de la semaine",
        "{hello} votre sélection de la semaine vous attend sur "
        "https://www.netflix.com/browse : [nouveaux films|séries "
        "québécoises|documentaires] et plus. Bonne écoute !\n\nNetflix",
    ),
    email(
        "support@apple.com",
        "Apple",
        "Aide et support",
        "{hello} notre page d'aide est disponible au "
        "https://www.apple.com/ca/fr/support. [N'hésitez pas à la consulter.|Vous "
        "y trouverez des guides pour votre appareil.]\n\nApple",
    ),
    email(
        "suivi@postescanada.ca",
        "Postes Canada",
        "Suivi de votre envoi",
        "{hello} vous pouvez suivre votre envoi n° {track} au "
        "https://www.postescanada.ca/suivi. Le colis avance bien.\n\nPostes Canada",
    ),
    email(
        "noreply@steampowered.com",
        "Steam",
        "Nouveautés de la semaine",
        "{hello} les nouveautés sont dans votre bibliothèque : "
        "https://steamcommunity.com/market. [Bonne découverte !|Bon jeu "
        "!]\n\nSteam",
    ),
    email(
        "comptes@amazon.ca",
        "Amazon.ca",
        "Vos commandes",
        "{hello} retrouvez l'historique de vos commandes au "
        "https://www.amazon.ca/gp/orders. [Merci !|Bonne journée !]\n\nAmazon.ca",
    ),
    email(
        "info@revenuquebec.ca",
        "Revenu Québec",
        "Services en ligne",
        "{hello} les services en ligne sont accessibles au "
        "https://www.revenuquebec.ca/citoyens. [Bonne journée !|Merci de votre "
        "confiance.]\n\nRevenu Québec",
    ),
    email(
        "noreply@microsoftonline.com",
        "Microsoft 365",
        "Votre boîte de courriel",
        "{hello} accédez à votre boîte au https://outlook.live.com/mail/ pour lire "
        "vos [messages|nouveaux messages].\n\nMicrosoft 365",
    ),
    # exceptions: legit mail with risky domains, http links or promo wording
    email(
        "info@club-echecs-hirondelles.info",
        "Club d'échecs des Hirondelles",
        "Calendrier des parties",
        "[Bonjour|Salut] les membres ! Le calendrier des parties de [mai|juin] est "
        "en ligne : http://club-echecs-hirondelles.info/[calendrier|parties]. "
        "[Rendez-vous {day} à {time}.|Bonne partie !]\n\nLe club d'échecs",
    ),
    email(
        "ligue@liguesoccerquartier.org",
        "Ligue de soccer du quartier",
        "Horaire des matchs",
        "L'horaire des matchs [de la saison|du mois] est affiché sur "
        "http://liguesoccerquartier.org/horaire. Premier match le {date} à "
        "[9 h|10 h 30|13 h].\n\nLa ligue",
    ),
    email(
        "{teacher[email]}",
        "{teacher[name]}",
        "Blogue de la classe",
        "Bonjour, les photos de [la sortie|l'expo-sciences|la classe verte] sont "
        "sur le blogue de la classe : http://blogue-[sec2|groupe3|classe-b204].xyz. "
        "[Bonne visite !|Laissez un commentaire !]\n\n{teacher[name]}",
        "{teacher[email]}",
    ),
    email(
        "coop@{school}",
        "La coop scolaire",
        "Vente de livres usagés",
        "Vente de livres usagés de la coop {day} : jusqu'à [40|50|60] % de rabais "
        "sur les romans et les manuels. Détails : "
        "http://coop-dessources.info[|/vente].\n\nLa coop",
    ),
    email(
        DIRECTION,
        "École secondaire",
        "Formulaire pour la sortie",
        "Bonjour, le formulaire d'autorisation pour la sortie au {museum} est ici : "
        "https://bit.ly/{code}. À remplir avant {day}.\n\nLa direction",
        DIRECTION,
    ),
    with_bounce(
        "info@infolettre-cuisine.com",
        "Infolettre Cuisine",
        "Recette vedette",
        "La recette vedette de la semaine : [lasagne|chili|soupe aux pois] en "
        "[20|30|45] minutes. Lire la suite : "
        "http://clic.infolettre-cuisine.com/r/{n4}\n\nL'équipe Cuisine du coin",
    ),
]

SPAM = [
    # prize
    email(
        "promo@concours-gratuit.top",
        "Concours Gratuit",
        "FÉLICITATIONS !!! VOUS AVEZ GAGNÉ !",
        "FÉLICITATIONS !!! VOUS AVEZ GAGNÉ [UN IPHONE GRATUIT|UNE TABLETTE "
        "GRATUITE|UNE CONSOLE GRATUITE] ! Pour réclamer votre prix, cliquez sur le "
        "lien ci-dessous dans les {hours} heures.\n\n"
        "http://concours-gratuit.top/[prix|reclamer|gagnant]\n\nCe concours est "
        "réservé aux participants chanceux.",
    ),
    email(
        "tirage@offres-express.info",
        "Tirage Express",
        "Gagnez une carte cadeau !",
        "Gagnez une carte cadeau de [50|100|200] $ chez [Amazon|Walmart|Best Buy] ! "
        "Participez à notre tirage en répondant à ce courriel avant "
        "[minuit|{day}].\n\nhttp://bit.ly/{code}",
    ),
    email(
        "voyages@voyages-etoiles.top",
        "Voyages Étoiles",
        "VOUS AVEZ ÉTÉ SÉLECTIONNÉ POUR UN VOYAGE GRATUIT !",
        "VOUS AVEZ ÉTÉ SÉLECTIONNÉ POUR UN VOYAGE GRATUIT [AUX CARAÏBES|EN "
        "FLORIDE|AU MEXIQUE|À CUBA] ! Répondez à ce courriel [avant {day}|dans les "
        "{hours} heures] pour réclamer votre prix.\n\nL'équipe Voyages Étoiles",
    ),
    email(
        "promo@tirage-magique.info",
        "Tirage Magique",
        "Concours : gagnez un abonnement d'un an !",
        "Concours : gagnez un abonnement [Netflix|Spotify|Disney+] pour un an ! "
        "C'est gratuit et facile. Cliquez ici pour participer.\n\n"
        "http://tirage-magique.info/[go|concours|{code}]",
    ),
    email(
        "concours@console-chance.xyz",
        "Console Chance",
        "Participez au tirage d'une console de jeux !",
        "Participez au tirage d'une console de jeux ! Un gagnant par "
        "[jour|semaine|mois]. La participation est gratuite.\n\n"
        "https://tinyurl.com/{code}",
    ),
    email(
        "cinema@cinema-plus.info",
        "Cinéma Plus",
        "GAGNEZ DES BILLETS DE CINÉMA !!!",
        "GAGNEZ DES BILLETS DE CINÉMA !!! [Répondez|Écrivez-nous] en {hours} heures pour "
        "avoir [une|la] chance de gagner un laissez-passer pour [deux|quatre|toute la "
        "famille].\n\nL'équipe Cinéma Plus",
    ),
    email(
        "offre@offre-express.top",
        "Offre Express",
        "Carte cadeau pour les premiers participants !",
        "[Offre spéciale|Offre du jour|Offre éclair] : carte cadeau de [25|50|75] $ pour les [50|100|200] "
        "premiers participants ! Cliquez vite avant que ce soit trop tard.\n\n"
        "http://offre-express.top",
    ),
    email(
        "webmaster@bonus-fantastique.tk",
        "Bonus Fantastique",
        "Vous êtes notre visiteur gagnant !",
        "Vous êtes le [100 000|500 000|1 000 000|10 000 000]e visiteur de notre site "
        "! Cliquez sur le lien pour réclamer votre prix gratuit "
        "[maintenant|avant minuit]. [C'est votre jour de chance.|Quelle chance !|]"
        "\n\nhttp://bonus-fantastique.tk",
    ),
    email(
        "rentree@rentree-chance.xyz",
        "Rentrée Chance",
        "Tirage de rentrée : tentez votre chance !",
        "[Tirage de rentrée|Grand tirage de la rentrée] : gagnez [une tablette gratuite|un ordinateur portable "
        "gratuit|des écouteurs gratuits|une montre intelligente gratuite] ! "
        "Inscrivez-vous avant le [15 août|31 août|5 septembre].\n\n"
        "http://rentree-chance.xyz",
    ),
    email(
        "sport@sport-chance.info",
        "Sport Chance",
        "Gagnez le chandail de votre équipe préférée !",
        "Gagnez le chandail de votre équipe préférée ! Concours gratuit pour tous "
        "les abonnés[| de l'infolettre]. [Tirage {day}.|Places limitées.]\n\n"
        "https://bit.ly/{code}",
    ),
    # discount
    email(
        "soldes@magasin-promo.info",
        "Magasin Promo",
        "MÉGA SOLDES : {pct} % de rabais sur tout !",
        "MÉGA SOLDES : {pct} % de rabais sur tout le magasin ! [Seulement cette fin "
        "de semaine.|Jusqu'à {day} seulement.] Achetez maintenant.\n\n"
        "http://magasin-promo.info",
    ),
    email(
        "solde@vetements-solde.top",
        "Vêtements Solde",
        "SOLDE DE FIN DE SAISON : jusqu'à {pct} % de rabais",
        "SOLDE DE FIN DE SAISON : jusqu'à {pct} % de rabais sur les "
        "[vêtements|chaussures|manteaux]. Les quantités sont limitées.\n\n"
        "http://vetements-solde.top",
    ),
    email(
        "jeux@jeux-offre.xyz",
        "Jeux Offre",
        "Offre de lancement : -{pct} % sur les nouveaux jeux !",
        "Offre de lancement : -{pct} % sur les nouveaux jeux vidéo [cette semaine "
        "seulement|jusqu'à {day}] !\n\nhttp://jeux-offre.xyz",
    ),
    email(
        "cinema@cinema-2pour1.info",
        "Cinéma Deux pour Un",
        "PROMOTION EXCLUSIVE : deux billets pour le prix d'un !",
        "PROMOTION EXCLUSIVE : deux billets pour le prix d'un [au cinéma du quartier|dans tous nos cinémas] "
        "[ce {day}|toute la semaine|pour les films de {time}] !\n\n"
        "http://cinema-2pour1.info",
    ),
    email(
        "rabais@librairies-rabais.top",
        "Librairies Rabais",
        "Rabais étudiants : {pct} % de rabais en librairie",
        "Rabais étudiants : {pct} % de rabais dans toutes les librairies "
        "participantes. [Montrez votre carte d'étudiant !|Valide jusqu'à {day}.|Sur "
        "présentation de la carte étudiante.]\n\n"
        "http://librairies-rabais.top",
    ),
    email(
        "vente@liquidation-vite.info",
        "Liquidation Vite",
        "SOLDES DE LIQUIDATION : tout à moitié prix !",
        "SOLDES DE LIQUIDATION : tout à moitié prix [pendant {hours} heures "
        "seulement|jusqu'à {day}] ! [Ne manquez pas ça.|Premier arrivé, premier servi.]\n\n"
        "http://liquidation-vite.info",
    ),
    email(
        "premier@premiers-achats.tk",
        "Premiers Achats",
        "Prix réduit de {pct} % pour les premiers achats !",
        "Prix réduit de {pct} % pour les [50|100|200] premiers achats de la semaine "
        "! Commandez maintenant.\n\nhttp://premiers-achats.tk",
    ),
    email(
        "smoothie@smoothies-offre.xyz",
        "Smoothies Offre",
        "2 pour 1 cette semaine !",
        "2 pour 1 sur les [smoothies|cafés glacés|jus frais] cette semaine "
        "seulement ! Offre valable [en magasin et en ligne|jusqu'à {day}].\n\n"
        "http://smoothies-offre.xyz",
    ),
    email(
        "musique@musique-rabais.info",
        "Musique Rabais",
        "Économisez {pct} % sur votre abonnement musical",
        "Économisez {pct} % sur votre prochain abonnement musical. [Une offre "
        "limitée pour les nouveaux membres.|Premier mois inclus.|Sans engagement.]\n\nhttp://musique-rabais.info",
    ),
    email(
        "pizza@pizza-special.top",
        "Pizza Spécial",
        "Pizza à prix réduit cette semaine !",
        "Pizza à [8 $ au lieu de 13 $|10 $ au lieu de 15 $|12 $ au lieu de 18 $] : "
        "l'offre de la semaine chez votre livreur préféré. Commandez avant [{day}|"
        "dimanche] !\n\nhttp://pizza-special.top",
    ),
    # promo phrasing
    email(
        "promo@boutique-lumineuse.xyz",
        "Boutique Lumineuse",
        "Achetez maintenant, les stocks sont limités !",
        "[Achetez maintenant|Achetez vite], les stocks sont limités ! Les [nouveautés|articles "
        "d'été|modèles vedettes] se vendent vite.\n\n"
        "http://boutique-lumineuse.xyz[|/nouveautes|/boutique]",
    ),
    email(
        "offre@occasion-vite.info",
        "Occasion Vite",
        "Offre limitée — expire dans {hours} heures !",
        "Offre limitée — expire dans {hours} heures ! [Ne laissez pas passer cette "
        "occasion.|Profitez-en pendant qu'il est temps.]\n\n"
        "http://occasion-vite.info[|/offre]",
    ),
    email(
        "games@games-deal.top",
        "Games Deal",
        "BUY NOW and save {pct} % on all games !",
        "BUY NOW and save {pct} % on all games ! [This week only.|Today only.]"
        "\n\nhttp://games-deal.top",
    ),
    email(
        "livraison@livraison-gratuite.info",
        "Livraison Gratuite",
        "Commandez avant minuit pour la livraison gratuite",
        "[Commandez avant minuit|Commandez maintenant] pour la livraison gratuite. [Dépêchez-vous, "
        "l'horloge tourne !|Plus que quelques heures !|Aucun minimum d'achat.]"
        "\n\nhttp://livraison-gratuite.info[|/commande]",
    ),
    email(
        "vedette@articles-vedettes.tk",
        "Articles Vedettes",
        "Dernière chance : quantités limitées !",
        "Dernière chance : quantités limitées sur les [articles vedettes|souliers "
        "de course|sacs à dos]. [Une fois partis, c'est fini.|Premier arrivé, "
        "premier servi.]\n\n"
        "http://articles-vedettes.tk[|/vedettes|/soldes]",
    ),
    email(
        "soir@offre-soir.xyz",
        "Offre Soir",
        "Ne manquez pas cette offre — elle se termine ce soir",
        "Ne manquez pas cette offre — elle se termine ce soir à [21 h|23 h "
        "59|minuit]. [Vraiment !|Pour de vrai !]\n\nhttp://offre-soir.xyz[|/offre|/ce-soir]",
    ),
    email(
        "deal@deal-special.info",
        "Deal Spécial",
        "Special deal just for you : -{pct} % de rabais aujourd'hui",
        "Special deal just for you : -{pct} % de rabais aujourd'hui seulement. "
        "[C'est votre jour de chance !|Ne tardez pas !]\n\nhttp://deal-special.info",
    ),
    email(
        "catalogue@catalogue-promo.top",
        "Catalogue Promo",
        "Prix de lancement : {pct} % de réduction sur tout",
        "Prix de lancement : {pct} % de réduction sur tout le catalogue. La promo "
        "dure une seule journée.\n\nhttp://catalogue-promo.top[|/lancement]",
    ),
    email(
        "reste@unites-restantes.info",
        "Unités Restantes",
        "Seulement {units} unités restantes à ce prix !",
        "Seulement {units} unités restantes à ce prix — [réservez vite avant d'être "
        "déçu|commandez avant qu'il soit trop tard] !\n\n"
        "http://unites-restantes.info[|/reserver]",
    ),
    email(
        "abo@abonnements-offre.xyz",
        "Abonnements Offre",
        "Offre de la semaine : {pct} % de moins sur tous les abonnements",
        "Offre de la semaine : {pct} % de moins sur tous les abonnements. Achetez "
        "maintenant, [c'est le bon moment|avant la hausse de prix] !\n\n"
        "http://abonnements-offre.xyz[|/abonnements]",
    ),
    # uppercase & exclamations
    email(
        "offer@super-offer.top",
        "Super Offer",
        "SUPER OFFER !!!! DONT MISS IT !!!!",
        "SUPER OFFER !!!! [DONT|DON'T] MISS IT !!!! [CLICK HERE|CLICK NOW|ACT NOW] !!!\n\n"
        "http://super-offer.top[|/deal|/now]",
    ),
    email(
        "vente@rabais-fou.xyz",
        "Rabais Fou",
        "OFFRE INCROYABLE !!! -{pct} % DE RABAIS SUR TOUT !!!",
        "OFFRE INCROYABLE !!! -{pct} % DE RABAIS SUR TOUT !!! [VENEZ VITE|FONCEZ|NE "
        "TARDEZ PAS] !!!\n\nhttp://rabais-fou.xyz",
    ),
    email(
        "promo@mega-vente.info",
        "Méga Vente",
        "PROFITEZ-EN !!! MÉGA VENTE !!!",
        "PROFITEZ-EN !!! MÉGA VENTE [DE LA SEMAINE|DU WEEK-END] !!! [TOUT DOIT "
        "DISPARAÎTRE|PRIX FOUS|STOCKS LIMITÉS] !!!\n\nhttp://mega-vente.info[|/vente|/mega]",
    ),
    email(
        "chance@chance-une.info",
        "Chance Unique",
        "NE MANQUEZ PAS CETTE CHANCE !!!",
        "NE MANQUEZ PAS CETTE CHANCE !!! [UNE SEULE JOURNÉE|{hours} HEURES "
        "SEULEMENT|DERNIER JOUR] !!!\n\nhttp://chance-une.info[|/offre|/vite]",
    ),
    email(
        "appareils@appareils-rabais.top",
        "Appareils Rabais",
        "ÉCONOMISEZ ÉNORMÉMENT !!! {pct} % DE RABAIS !!!",
        "ÉCONOMISEZ ÉNORMÉMENT !!! {pct} % DE RABAIS SUR LES "
        "[APPAREILS|TÉLÉVISEURS|ORDINATEURS] !!!\n\nhttp://appareils-rabais.top",
    ),
    email(
        "promo@promo-vite.xyz",
        "Promo Vite",
        "CLIQUEZ MAINTENANT !!! LA PROMO SE TERMINE BIENTÔT !!!",
        "[CLIQUEZ MAINTENANT|CLIQUEZ ICI] !!! LA PROMO SE TERMINE [BIENTÔT|CE SOIR|DEMAIN] !!!"
        "\n\nhttp://promo-vite.xyz[|/promo|/go]",
    ),
    email(
        "echantillon@echantillons-gratuit.tk",
        "Échantillons Gratuit",
        "GRATUIT !!! GRATUIT !!! GRATUIT !!!",
        "GRATUIT !!! GRATUIT !!! GRATUIT !!! Des [échantillons|cadeaux|surprises] "
        "pour [tous|vous] !!!\n\nhttp://echantillons-gratuit.tk[|/gratuit|/cadeau]",
    ),
    email(
        "surprise@surprises-quotidiennes.info",
        "Surprises Quotidiennes",
        "WOW !!! Des surprises chaque jour !!!",
        "[WOW|OUAH] !!! Des surprises chaque [jour|semaine] !!! Inscrivez-vous "
        "[aujourd'hui|maintenant] !!!\n\nhttp://surprises-quotidiennes.info[|/wow]",
    ),
    # multiple links
    email(
        "promo@rabais-multiples.info",
        "Rabais Multiples",
        "Trois sites, trois rabais !",
        "[Trois sites, trois rabais|Trois fois plus de rabais] : http://rabais-un.info, http://rabais-deux.top "
        "et http://rabais-trois.xyz. [Visitez-les|Allez-y] avant [la fin de la "
        "semaine|{day}|minuit] !",
    ),
    email(
        "info@magasin-officiel.info",
        "Magasin Officiel",
        "Retrouvez-nous partout !",
        "Retrouvez-nous partout : https://bit.ly/{code}, https://tinyurl.com/{code2} "
        "et http://magasin-officiel.info. Bon magasinage !",
    ),
    email(
        "vente@prix-choc.info",
        "Prix Choc",
        "Comparez nos prix !",
        "[Comparez nos prix|Voyez par vous-même|Faites le test] : http://prix-bas.xyz, "
        "http://prix-fous.top et http://prix-choc.info. [Le meilleur prix est chez "
        "nous|Nos prix sont imbattables][ !| — garanti !| cette semaine !]",
    ),
    email(
        "pages@pages-promo.tk",
        "Pages Promo",
        "Quatre pages à visiter !",
        "[Nos pages à visiter|Visitez nos pages|À voir] : http://page1-promo.tk, http://page2-promo.info, "
        "http://page3-promo.xyz et http://page4-promo.top. Quatre chances de rabais "
        "[cette semaine|avant {day}] !",
    ),
    email(
        "offre@lien-trois.top",
        "Lien Trois",
        "L'offre complète est ici !",
        "[L'offre complète est ici|Tous les détails|Choisissez votre lien] : http://lien-un.xyz, "
        "http://lien-deux.info et http://lien-trois.top. C'est votre "
        "[semaine|journée|soirée] de chance ![| Ne tardez pas.]",
    ),
    # English
    email(
        "money@free-money.top",
        "Free Money",
        "FREE MONEY NOW — CLICK HERE",
        "FREE MONEY NOW — CLICK HERE to claim your [PRIZE|CASH|REWARD] !\n\n"
        "http://free-money.top[|/claim|/{code}]",
    ),
    email(
        "gift@win-gift.info",
        "Win Gift",
        "WIN a FREE GIFT — LIMITED TIME",
        "WIN a FREE [GIFT|PHONE|GIFT CARD] — LIMITED TIME, [CLICK NOW|CLICK HERE] !!!\n\n"
        "http://win-gift.info[|/win|/gift]",
    ),
    email(
        "store@exclusive-offer.xyz",
        "Exclusive Offer",
        "EXCLUSIVE OFFER — {pct} % DISCOUNT",
        "EXCLUSIVE OFFER — {pct} % DISCOUNT on all items, [BUY NOW|SHOP NOW] !\n\n"
        "http://exclusive-offer.xyz",
    ),
    email(
        "ship@free-shipping.top",
        "Free Shipping",
        "HURRY ! Only {hours} hours left !",
        "HURRY ! Only {hours} hours left ! FREE shipping on [everything|all "
        "orders|all items] !\n\nhttp://free-shipping.top",
    ),
    email(
        "deal@amazing-deal.info",
        "Amazing Deal",
        "AMAZING DEAL ! Get {units} for the price of 1 !",
        "AMAZING DEAL ! Get {units} for the price of 1 ! Order [today|now] !\n\n"
        "http://amazing-deal.info[|/deal]",
    ),
    email(
        "stock@limited-stock.tk",
        "Limited Stock",
        "DON'T WAIT ! LIMITED STOCK !",
        "DON'T WAIT ! [LIMITED STOCK|ALMOST SOLD OUT] ! Special price for [you|today|members] !\n\n"
        "http://limited-stock.tk[|/deal|/now]",
    ),
    # misc
    email(
        "cours@anglais-rapide.top",
        "Anglais Rapide",
        "Apprenez l'anglais en un temps record !",
        "Apprenez l'anglais en [10|15|30] jours, [garanti, sans effort|sans effort, garanti] ! Appelez "
        "maintenant au 1-800-555-0[100|123|199].\n\nhttp://anglais-rapide.top",
    ),
    email(
        "forfait@forfait-super.xyz",
        "Forfait Super",
        "Plus de données pour le même prix !",
        "Votre nouveau forfait téléphonique : [3|4|5] fois plus de données pour le "
        "même prix ! Offre valable [cette semaine|jusqu'à {day}].\n\n"
        "http://forfait-super.xyz",
    ),
    email(
        "musique@musique-1dollar.info",
        "Musique à 1 $",
        "Votre musique préférée pour 1 $ par mois !",
        "Écoutez votre musique préférée pour 1 $ par mois pendant [3|4|6] mois ! "
        "[Nouveaux membres seulement.|Annulez en tout temps.]\n\n"
        "http://musique-1dollar.info[|/essai|/membres]",
    ),
    email(
        "emploi@emploi-simple.top",
        "Emploi Simple",
        "Emploi d'été payant, sans expérience !",
        "Emploi d'été : gagnez [20|25|30] $ de l'heure [à la maison|en ligne|de chez "
        "vous] ! [Aucune expérience requise.|Horaire flexible.] Inscrivez-vous vite.\n\nhttp://emploi-simple.top",
    ),
    email(
        "affaires@bonbons-riches.xyz",
        "Bonbons Riches",
        "Devenez riche en vendant des bonbons !",
        "[Devenez riche|Faites fortune] en vendant des bonbons ! Notre programme "
        "vous montre comment. Commencez [aujourd'hui|dès {day}].\n\n"
        "http://bonbons-riches.xyz",
    ),
    email(
        "appli@marche-payante.info",
        "Marche Payante",
        "La nouvelle application qui vous paie pour marcher !",
        "[La nouvelle application|L'application] qui vous paie pour marcher ! [Jusqu'à [50|100] $ "
        "par mois. |]Téléchargez-la gratuitement.\n\nhttp://marche-payante.info"
        "[|/app|/marche]",
    ),
    email(
        "diplome@diplome-express.tk",
        "Diplôme Express",
        "Obtenez votre diplôme sans examen !",
        "[Obtenez|Décrochez] votre diplôme en [10|15|30] jours, sans examen ! "
        "[Appelez maintenant.|Inscription en ligne.]\n\n"
        "http://diplome-express.tk[|/inscription]",
    ),
    # exceptions: clean domains, https or no link
    email(
        "promo@boutique-mode.ca",
        "Boutique Mode",
        "Soldes d'été sur les maillots",
        "Soldes d'été : {pct} % de rabais sur les [maillots|sandales|lunettes de "
        "soleil]. Magasinez sur https://www.boutique-mode.ca[|/soldes] avant "
        "{day}.\n\nBoutique Mode",
    ),
    email(
        "offres@voyages-soleil.com",
        "Voyages Soleil",
        "Offre exclusive : une semaine au soleil",
        "Offre exclusive : une semaine [à Cuba|au Mexique|en Floride] à partir de "
        "[799|899|999] $ par personne[|, vol inclus]. Réservez [avant {day}|dès "
        "maintenant] sur "
        "https://voyages-soleil.com/offres.\n\nVoyages Soleil",
    ),
    email(
        "info@abonnement-jeux.com",
        "Club Jeux Plus",
        "Votre premier mois à 1 $",
        "Abonnez-vous au Club Jeux Plus : [un nouveau jeu|deux jeux|trois jeux] par "
        "mois, premier mois à 1 $[| puis {amount}]. [Annulez en tout temps.|] Répondez [OUI|« JE M'ABONNE »] à ce courriel pour "
        "commencer.",
    ),
    email(
        "ventes.rapides{n3}@gmail.com",
        "[Marc|Julie|Kevin]",
        "Écouteurs neufs à [15|20|25] $",
        "Je vends des [écouteurs sans fil|montres intelligentes|haut-parleurs] "
        "neufs à [15|20|25] $, livraison gratuite. Écrivez-moi [vite|aujourd'hui], "
        "quantités limitées !",
    ),
]

PHISHING = [
    # bait-word domains
    email(
        "securite@desjardins-verification.info",
        "Service Desjardins",
        "Votre compte a été bloqué",
        "{dear} votre compte Desjardins a été bloqué [suite à une activité "
        "inhabituelle|après plusieurs tentatives de connexion]. Vérifiez votre "
        "identité [dès maintenant|dans les {hours} heures] : "
        "http://desjardins-verification.info[|/login|/identite]\n\nService "
        "Desjardins",
    ),
    email(
        "info@netflix-billing.tk",
        "Netflix",
        "Problème de paiement",
        "{dear} nous avons détecté une tentative de connexion suspecte sur votre "
        "compte Netflix[| le {date}]. Confirmez vos informations de paiement : "
        "http://netflix-billing.tk/update.php\n\nNetflix",
    ),
    email(
        "support@amazon-security-login.com",
        "Amazon Support",
        "Votre compte Amazon a été suspendu",
        "{dear} votre compte Amazon a été suspendu[| le {date}]. Pour le réactiver, "
        "connectez-vous [sans tarder|dans les {hours} heures] sur "
        "http://amazon-security-login.com\n\nAmazon Support",
    ),
    email(
        "livraison@postes-canada-suivi.info",
        "Postes Canada",
        "Un colis vous attend",
        "{dear} un colis vous attend[| depuis le {date}]. Veuillez confirmer votre "
        "adresse pour la livraison : http://postes-canada-suivi.info\n\nPostes "
        "Canada",
    ),
    email(
        "remboursement@revenu-quebec-remboursement.top",
        "Revenu Québec",
        "Vous avez droit à un remboursement",
        "{dear} vous avez droit à un remboursement de {amount}. Cliquez pour le "
        "recevoir : http://revenu-quebec-remboursement.top\n\nRevenu Québec",
    ),
    email(
        "verification@microsoft-account-verify.net",
        "Microsoft 365",
        "Vérification de votre identifiant",
        "{dear} votre identifiant Microsoft doit être vérifié avant {hours} heures "
        ": http://microsoft-account-verify.net[|/verify]\n\nMicrosoft 365",
    ),
    email(
        "support@apple-id-verify.tk",
        "Apple Support",
        "Problème de paiement sur votre compte",
        "{dear} problème de paiement sur votre compte Apple[| pour un achat de "
        "{amount}]. Régularisez-le [ici|sans tarder] : http://apple-id-verify.tk"
        "\n\nApple Support",
    ),
    email(
        "service@paypal-verification.info",
        "PayPal",
        "Votre compte PayPal est limité",
        "{dear} votre compte PayPal est limité. Retirez la limite en confirmant vos "
        "informations[| d'ici {day}] : http://paypal-verification.info\n\nPayPal",
    ),
    email(
        "factures@hydro-quebec-facture.info",
        "Hydro-Québec",
        "Votre facture est impayée",
        "{dear} votre facture Hydro-Québec[| de {amount}] est impayée. Évitez la "
        "coupure en payant [ici|avant {day}] : http://hydro-quebec-facture.info"
        "\n\nHydro-Québec",
    ),
    email(
        "alerte@steam-verification.tk",
        "Steam Support",
        "Alerte de sécurité sur votre compte",
        "{dear} alerte de sécurité sur votre compte Steam[| depuis un nouvel "
        "appareil]. Vérifiez votre session[| dans les {hours} heures] : "
        "http://steam-verification.tk\n\nSteam Support",
    ),
    # character substitution
    email(
        "noreply@amaz0n.com",
        "Amazon",
        "Mise à jour de vos informations",
        "{dear} veuillez mettre à jour vos informations de connexion sur "
        "amaz0n.com pour éviter la suspension de votre compte[| d'ici {hours} "
        "heures].\n\nAmazon",
    ),
    email(
        "support@rnicrosoft.com",
        "Microsoft Support",
        "Connexion depuis un nouvel appareil",
        "{dear} nous avons remarqué une connexion depuis un nouvel appareil[| le "
        "{date}| à {time}]. Confirmez-la sur rnicrosoft.com.\n\nMicrosoft Support",
    ),
    email(
        "service@paypa1.com",
        "PayPal",
        "Votre session a expiré",
        "{dear} votre session paypa1.com a expiré. Connectez-vous pour continuer "
        "vos achats[| en toute sécurité].\n\nPayPal",
    ),
    email(
        "equipe@micr0soft.com",
        "Équipe Microsoft",
        "Confirmation de votre courriel",
        "{dear} confirmez votre courriel sur micr0soft.com pour garder l'accès à "
        "votre boîte[| dans les {hours} heures].\n\nÉquipe Microsoft",
    ),
    email(
        "info@netf1ix.com",
        "Netflix",
        "Renouvellement de votre abonnement",
        "{dear} votre abonnement se renouvelle automatiquement le {date}. Gérez-le "
        "sur netf1ix.com.\n\nNetflix",
    ),
    email(
        "accesd@desjard1ns.com",
        "Service Desjardins",
        "Frais inhabituels détectés",
        "{dear} des frais inhabituels de {amount} ont été détectés. Vérifiez vos "
        "relevés sur accesd.desjard1ns.com.\n\nService Desjardins",
    ),
    email(
        "securite@st3am.com",
        "Steam",
        "Votre compte de jeu est à risque",
        "{dear} votre compte de jeu est à risque. Protégez-le sur st3am.com[| avant "
        "{day}| dès maintenant].\n\nSteam",
    ),
    email(
        "alertes@app1e.com",
        "Apple",
        "Achat non reconnu",
        "{dear} un achat de {amount} a été effectué. Ce n'est pas vous ? "
        "Signalez-le sur app1e.com.\n\nApple",
    ),
    # domain-end trap
    email(
        "securite@desjardins.com.securite-client.xyz",
        "Service Desjardins",
        "Votre accès sera fermé",
        "{dear} votre accès sera fermé si vous ne répondez pas[| d'ici {hours} "
        "heures] : http://desjardins.com.securite-client.xyz[|/acces|/login]"
        "\n\nService Desjardins",
    ),
    email(
        "support@amazon.com.verify-login.top",
        "Amazon",
        "Réactivez votre compte",
        "{dear} réactivez votre compte[| avant {day}] : "
        "http://amazon.com.verify-login.top[|/signin|/reactiver]\n\nAmazon",
    ),
    email(
        "comptes@netflix.com.account-update.info",
        "Netflix",
        "Votre paiement est en attente",
        "{dear} votre paiement[| de {amount}] est en attente : "
        "http://netflix.com.account-update.info\n\nNetflix",
    ),
    email(
        "verification@microsoft.com.connexion-securisee.xyz",
        "Microsoft 365",
        "Vérification requise",
        "{dear} vérification requise[| avant {day}| dans les {hours} heures] : "
        "http://microsoft.com.connexion-securisee.xyz\n\nMicrosoft 365",
    ),
    email(
        "suivi@postescanada.ca.suivi-livraison.info",
        "Postes Canada",
        "Votre colis ne peut pas être livré",
        "{dear} votre colis[| n° {track}] ne peut pas être livré : "
        "http://postescanada.ca.suivi-livraison.info\n\nPostes Canada",
    ),
    # links: IP, shorteners, HTTP
    email(
        "securite@desjardins.com",
        "Service Desjardins",
        "Connexion depuis une adresse inconnue",
        "{dear} votre compte a été utilisé depuis une adresse inconnue. Vérifiez "
        "ici : http://{ip}/desjardins/login\n\nService Desjardins",
    ),
    email(
        "remboursement@revenuquebec.ca",
        "Revenu Québec",
        "Récupérez votre remboursement",
        "{dear} cliquez pour récupérer votre remboursement[| de {amount}] : "
        "https://bit.ly/{code}\n\nRevenu Québec",
    ),
    email(
        "service@paypal.com",
        "PayPal",
        "Sécurisez votre compte",
        "{dear} sécurisez votre compte PayPal : http://{ip}/paypal/secure\n\nPayPal",
    ),
    email(
        "support@apple.com",
        "Apple Support",
        "Mettez à jour vos informations",
        "{dear} mettez à jour vos informations : http://{ip}/apple/id-verify\n\n"
        "Apple Support",
    ),
    email(
        "verification@microsoft.com",
        "Microsoft 365",
        "Votre mot de passe expire bientôt",
        "{dear} votre mot de passe expire [bientôt|dans {hours} heures]. "
        "Renouvelez-le : http://micr0soft-alert.com/verify\n\nMicrosoft 365",
    ),
    email(
        "livraison@postescanada.ca",
        "Postes Canada",
        "Confirmez votre adresse de livraison",
        "{dear} confirmez votre adresse de livraison : "
        "http://postescanada-suivi.info/paiement?ref={n4}\n\nPostes Canada",
    ),
    email(
        "comptes@bmo.com",
        "BMO",
        "Accédez à votre relevé",
        "{dear} accédez à votre relevé[| de {month}] : https://tinyurl.com/{code}"
        "\n\nBMO",
    ),
    email(
        "support@amazon.ca",
        "Amazon",
        "Sécurisez votre compte",
        "{dear} [une connexion inhabituelle a été détectée|des modifications ont "
        "été apportées à votre profil]. Sécurisez votre compte : "
        "http://amazon.ca.security-check.xyz/login\n\nAmazon",
    ),
    email(
        "accesd@desjardins.com",
        "Desjardins",
        "Votre session a expiré",
        "{dear} votre session a expiré[| à {time}]. Connectez-vous à nouveau[| pour "
        "éviter le blocage] : http://accesd-desjardins-verification.top\n\n"
        "Desjardins",
    ),
    # displayed name vs address
    email(
        "support{n3}@gmail.com",
        "Amazon Support",
        "Compte bloqué",
        "{dear} votre compte est bloqué. Cliquez pour le réactiver : "
        "https://bit.ly/{code}",
    ),
    email(
        "securite@desjardins-verification.info",
        "Service Desjardins",
        "Vérification de sécurité requise",
        "{dear} vérification de sécurité requise sur votre compte AccèsD. Agissez "
        "[rapidement|dans les {hours} heures] pour éviter le blocage[| de vos "
        "cartes].",
    ),
    email(
        "support.microsoft.security@gmail.com",
        "Microsoft Support",
        "Votre session a expiré",
        "{dear} votre session a expiré[| le {date}]. Renouvelez-la pour continuer à "
        "utiliser votre boîte de courriel[| sans interruption].",
    ),
    email(
        "info@netflix-billing.tk",
        "Netflix",
        "Problème de paiement",
        "{dear} un problème de paiement est survenu sur votre compte[| le {date}]. "
        "Mettez à jour votre moyen de paiement ici : "
        "http://netflix-billing.tk/update.php",
    ),
    email(
        "livraison@postes-canada-suivi.info",
        "Postes Canada",
        "Un colis vous attend",
        "{dear} un colis vous attend au bureau de poste[| depuis {day}]. Confirmez "
        "votre adresse pour la livraison : http://postes-canada-suivi.info",
    ),
    email(
        "service@paypa1.com",
        "PayPal Service",
        "Compte limité",
        "{dear} votre compte est limité jusqu'à confirmation de vos informations. "
        "Connectez-vous pour retirer la limite[| d'ici {day}| dans les {hours} "
        "heures].",
    ),
    email(
        "apple.service.alert@hotmail.com",
        "Apple Support",
        "Votre identifiant doit être vérifié",
        "{dear} votre identifiant Apple doit être vérifié avant [la fin de la "
        "semaine|{day}|le {date}]. Cliquez ici pour continuer : "
        "http://apple.id-verify.top/signin",
    ),
    email(
        "factures@hydroquebec-info.xyz",
        "Hydro-Québec",
        "Facture impayée",
        "{dear} votre facture de {amount} est impayée. Évitez les frais en réglant "
        "votre solde : http://hydroquebec-info.xyz/paiement",
    ),
    # Return-Path / Reply-To
    email(
        "securite@desjardins.com",
        "Service Desjardins",
        "Alerte de sécurité sur votre compte",
        "{dear} alerte de sécurité sur votre compte AccèsD[| le {date}]. Veuillez "
        "vous connecter et vérifier vos transactions récentes.\n\nService "
        "Desjardins",
        "<x{n4}@relais-etranger.info>",
    ),
    email(
        "support@microsoft.com",
        "Microsoft Support",
        "Votre compte a été utilisé",
        "{dear} votre compte a été utilisé depuis un autre appareil[| à {time}| le "
        "{date}]. Consultez votre historique de connexion.\n\nMicrosoft Support",
        "<bulk{n3}@ms-alert.info>",
        "<recovery@mail.com>",
    ),
    email(
        "facturation@fournisseur.ca",
        "Fournisseur.ca",
        "Confirmation de facturation",
        "Bonjour, votre facture [du mois|de {month}] est prête. Le paiement de "
        "{amount} est dû avant le [15|30] du mois.\n\nFournisseur.ca",
        "<facturation@fournisseur.ca>",
        "<paiements@fournisseur-inv.top>",
    ),
    email(
        "no-reply@netflix.com",
        "Netflix",
        "Paiement en attente",
        "{dear} votre paiement est en attente. Mettez à jour votre mode de "
        "paiement pour continuer à regarder[| vos séries].\n\nNetflix",
        "<bounce-{n3}@netflix-billing.tk>",
    ),
    email(
        "noreply@hydroquebec.com",
        "Hydro-Québec",
        "Remboursement disponible",
        "{dear} un remboursement de {amount} est disponible sur votre compte. "
        "Communiquez avec nous pour le recevoir.\n\nHydro-Québec",
        "<refund@factures-quebec.info>",
    ),
    email(
        "info@postescanada.ca",
        "Postes Canada",
        "Colis en attente de livraison",
        "{dear} votre colis[| n° {track}] est en attente de livraison. Confirmez "
        "votre adresse pour finaliser l'envoi.\n\nPostes Canada",
        "<livraison@suivi-poste.top>",
        "<livraison@suivi-poste.top>",
    ),
    # bad sender domain, benign body
    email(
        "securite@desjardins-verification.info",
        "Desjardins",
        "Connexion à votre compte AccèsD",
        "{hello} nous avons remarqué une connexion à votre compte AccèsD depuis un "
        "appareil que vous ne reconnaissez pas[| le {date}]. Pour votre sécurité, "
        "veuillez consulter vos relevés et nous aviser de toute anomalie.\n\nMerci "
        "de votre confiance.",
    ),
    email(
        "noreply@microsoft-account-verify.net",
        "Microsoft",
        "Votre abonnement Microsoft 365",
        "{hello} votre abonnement Microsoft 365 arrive à échéance[| le {date}]. Les "
        "détails de votre facture sont disponibles sur le portail. Bonne journée.",
    ),
    email(
        "comptes@netflix-billing.tk",
        "Netflix",
        "Mise à jour de votre facturation",
        "{hello} la facturation de votre compte a été mise à jour[| le {date}]. "
        "Vous pouvez consulter le résumé de votre abonnement en tout temps.",
    ),
    email(
        "service@paypa1.com",
        "PayPal",
        "Votre compte est à jour",
        "{hello} nous vous remercions de votre confiance. Votre compte est à "
        "jour[| depuis le {date}]. Pour toute question, communiquez avec nous.",
    ),
    email(
        "no-reply@amaz0n.com",
        "Amazon",
        "Votre commande a bien été reçue",
        "{hello} votre commande [de la semaine|n° {order}] a bien été reçue. Un "
        "courriel de confirmation séparé vous sera envoyé. Merci.",
    ),
    email(
        "alerte@bmo-securite.xyz",
        "BMO",
        "Utilisation de votre carte",
        "{hello} votre carte [se terminant par {n4} |]a été utilisée récemment. "
        "Aucune action n'est requise. Bonne journée.",
    ),
    email(
        "suivi@postescanada-livraison.xyz",
        "Postes Canada",
        "Envoi en transit",
        "{hello} un envoi est en transit vers votre adresse. Le suivi sera mis à "
        "jour [dans les prochaines heures|d'ici {day}].",
    ),
    email(
        "info@revenu-quebec-verification.info",
        "Revenu Québec",
        "Votre dossier est en traitement",
        "{hello} votre dossier [n° {order} |]est en cours de traitement. Les "
        "documents demandés ont bien été reçus. Merci de votre collaboration.",
    ),
    # school
    email(
        "securite@dessources-verification.xyz",
        "Portail scolaire",
        "Votre compte sera fermé",
        "{hello} votre compte du portail scolaire sera fermé dans {hours} heures si "
        "vous ne confirmez pas votre identité : "
        "http://dessources-verification.xyz/portail",
    ),
    email(
        "noreply@bibliotheque-numerique.tk",
        "Bibliothèque numérique",
        "Emprunt numérique en retard",
        "{hello} votre emprunt numérique « {book} » est en retard. Réinitialisez "
        "votre mot de passe ici : http://bibliotheque-numerique.tk/reinitialiser",
    ),
    email(
        "direction@dessources.qc.ca.connexion.top",
        "Direction",
        "Mise à jour de vos informations",
        "{hello} la direction vous demande de mettre à jour vos informations pour "
        "[la trousse d'urgence|le dossier médical|la sortie du {date}] : "
        "http://dessources.qc.ca.connexion.top",
    ),
    email(
        "helpdesk@dessources-message.info",
        "Équipe informatique",
        "Votre boîte est presque pleine",
        "{hello} votre boîte de courriel est pleine à [92|95|98|99] %. Libérez de "
        "l'espace ou agrandissez-la ici : http://dessources-message.info/boite",
    ),
    # exceptions: no link, asks for a reply
    email(
        "portail.dessources[|.aide]@gmail.com",
        "Portail scolaire",
        "Votre mot de passe expire aujourd'hui",
        "{hello} votre mot de passe du portail scolaire expire aujourd'hui. "
        "Répondez à ce courriel avec votre nom d'utilisateur et votre mot de passe "
        "actuel pour le conserver.[| Merci.]",
    ),
    email(
        "direction.dessources@[outlook.com|hotmail.com]",
        "Direction de l'école",
        "Petit service rapide",
        "{hello} je suis en réunion et j'ai besoin d'un petit service. Pouvez-vous "
        "acheter [2|3|4] cartes-cadeaux de [25|50] $ et m'envoyer les codes par "
        "courriel ? Je vous rembourse [demain|{day}].\n\nLa direction",
    ),
    email(
        "service@desjardins.com",
        "Service Desjardins",
        "Confirmation de votre carte",
        "{dear} pour confirmer votre carte, répondez à ce courriel avec le numéro "
        "de la carte et sa date d'expiration[| d'ici {hours} heures].\n\nService "
        "Desjardins",
        "",
        "<verification@desjardins-aide.info>",
    ),
]


TEMPLATES = {"ham": HAM, "spam": SPAM, "phishing": PHISHING}


def draw(template, seen, attempts=100):
    """Row with an unseen message, or None if the template is exhausted."""
    for _ in range(attempts):
        slots = {key: make() for key, make in SLOTS.items()}
        row = {
            field: render(text, slots)
            for field, text in zip_longest(HEADERS, template, fillvalue="")
        }
        if row["message"] not in seen:
            seen.add(row["message"])
            return row
    return None


def generate(counts, templates, seen):
    rows = []
    for label, count in counts.items():
        pool, made = list(templates[label]), 0
        while made < count:
            if not pool:
                sys.exit(f"{label} : variantes épuisées après {made} courriels")
            for template in list(pool):
                row = draw(template, seen)
                if row is None:
                    pool.remove(template)
                    continue
                rows.append({**row, "label": label})
                made += 1
                if made == count:
                    break
        if dropped := len(templates[label]) - len(pool):
            print(
                f"Attention : {dropped}/{len(templates[label])} modèles {label} "
                "épuisés, les autres sont surreprésentés",
                file=sys.stderr,
            )
    return rows


def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for label in TEMPLATES:
        parser.add_argument(f"--{label}", type=int, default=0, metavar="N")
    parser.add_argument(
        "--test-share",
        type=float,
        default=0,
        metavar="P",
        help="share of each label moved to a test set from held-out templates",
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="default: datasets/emails_<total>.csv"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    counts = {label: getattr(args, label) for label in TEMPLATES}
    if sum(counts.values()) <= 0:
        parser.error(
            "donnez au moins un nombre de courriels (--ham, --spam, --phishing)"
        )
    if not 0 <= args.test_share < 1:
        parser.error("--test-share doit être dans [0, 1[")
    output = args.output or DATASETS / f"emails_{sum(counts.values())}.csv"

    random.seed(args.seed)
    seen = set()
    if args.test_share:
        step = max(2, round(1 / args.test_share))  # every step-th template
        held_out = {label: t[step - 1 :: step] for label, t in TEMPLATES.items()}
        train_templates = {
            label: [x for x in t if x not in held_out[label]]
            for label, t in TEMPLATES.items()
        }
        test_counts = {k: round(n * args.test_share) for k, n in counts.items()}
        test = generate(test_counts, held_out, seen)
        random.shuffle(test)  # label order would leak the key
        for i, row in enumerate(test, 1):
            row["id"] = i
        counts = {k: n - test_counts[k] for k, n in counts.items()}
        test_path = output.with_name(f"{output.stem}_test.csv")
        key_path = output.with_name(f"{output.stem}_test_labels.csv")
        write(test_path, test, ["id", *HEADERS])
        write(key_path, test, ["id", "label"])
    else:
        train_templates = TEMPLATES
    rows = generate(counts, train_templates, seen)
    write(output, rows, [*HEADERS, "label"])

    print(f"Total      : {len(rows)}")
    print(f"Labels     : {dict(Counter(r['label'] for r in rows))}")
    print(
        f"ReturnPath : {sum(1 for r in rows if r['return_path'])}   "
        f"Reply-To : {sum(1 for r in rows if r['reply_to'])}"
    )
    print(f"Avec lien  : {sum(1 for r in rows if 'http' in r['message'])}")
    print(f"Fichier    : {output}")
    if args.test_share:
        print(f"Test       : {len(test)} {dict(Counter(r['label'] for r in test))}")
        print(f"Fichiers   : {test_path}, {key_path} (clé, ne pas publier)")


if __name__ == "__main__":
    main()
