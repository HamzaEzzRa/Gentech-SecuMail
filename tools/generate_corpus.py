import csv
import random
from pathlib import Path

random.seed(42)

OUTPUT = Path(__file__).resolve().parent.parent / "datasets" / "emails_1000.csv"

SCHOOL_DOMAIN = "dessources.qc.ca"

FIRST_NAMES_F = ["Émilie", "Juliette", "Rosalie", "Léa", "Florence", "Camille",
             "Maëlle", "Laurence", "Béatrice", "Sophie", "Amélie", "Noémie",
             "Charlotte", "Zoé", "Annabelle"]
FIRST_NAMES_M = ["Simon", "Gabriel", "Félix", "William", "Thomas", "Nathan",
             "Antoine", "Olivier", "Charles", "Louis", "Édouard", "Jacob",
             "Raphaël", "Émile", "Lucas"]
LAST_NAMES = ["Tremblay", "Gagnon", "Roy", "Côté", "Bouchard", "Gauthier", "Morin",
        "Lavoie", "Fortin", "Gagné", "Ouellet", "Pelletier", "Bélanger",
        "Lévesque", "Bergeron", "Leblanc", "Girard", "Fournier", "Caron",
        "Dubois", "Boisvert"]
TEACHERS = ["M. Bergeron", "Mme Fortin", "M. Gagnon", "Mme Lavoie", "M. Roy",
         "Mme Bélanger", "M. Caron", "Mme Girard", "M. Pelletier",
         "Mme Morin"]
SUBJECTS = ["mathématiques", "français", "sciences", "histoire", "anglais",
            "éducation physique", "arts plastiques", "musique", "informatique"]

MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin"]
DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]

KEYWORDS = ["devoirs", "examen", "projet", "réunion", "remise", "sortie",
            "entraînement", "pratique", "tournoi", "concours", "inscription",
            "rencontre", "laboratoire", "bibliothèque", "voyage", "camp"]


def student_email():
    """Student address: first.last@dessources.qc.ca."""
    first_name = random.choice(FIRST_NAMES_F + FIRST_NAMES_M)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name.lower()}.{last_name.lower()}@dessources.qc.ca"


def random_first_name():
    return random.choice(FIRST_NAMES_F + FIRST_NAMES_M)


def random_full_name():
    first_name = random.choice(FIRST_NAMES_F + FIRST_NAMES_M)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def random_teacher():
    return random.choice(TEACHERS)


def random_subject():
    return random.choice(SUBJECTS)


def random_day():
    return random.choice(DAYS)


def random_month():
    return random.choice(MONTHS)


def random_day_month():
    return f"{random.randint(1, 28)} {random.choice(MONTHS)}"


def full_subject():
    """Email subject line."""
    return f"{random.choice(['Rappel', 'Info', 'Avis', 'Note'])}, " \
           f"{random.choice(KEYWORDS)} — voir message."


ROWS = []


def add(sender, name, subject, body, return_path="", reply_to="", label="ham"):
    ROWS.append({
        "sender": sender,
        "name": name,
        "subject": subject,
        "message": body,
        "return_path": return_path,
        "reply_to": reply_to,
        "label": label,
    })


# HAM — school admin
HAM_ADMIN = [
    (lambda: f"Bonjour, petit rappel : les devoirs de {random_subject()} doivent être "
             f"remis {random_day()}. Bonne semaine !\n\n{random_teacher()}",
     "Rappel des devoirs"),
    (lambda: "Avis aux élèves : l'école fermera à 15 h mercredi pour une "
             "réunion des enseignants. Les autobus partiront à 15 h 15.\n\n"
             "La direction",
     "Fermeture hâtive mercredi"),
    (lambda: "Rappel de la bibliothèque : le livre que vous avez emprunté doit "
             "être retourné d'ici vendredi. Merci !\n\nMme Fortin, bibliothécaire",
     "Livre à retourner"),
    (lambda: "Entraînement de hockey demain à 16 h au gymnase. N'oubliez pas "
             "votre casque et votre bouteille d'eau. On compte sur vous !\n\nM. Roy",
     "Pratique de hockey"),
    (lambda: f"La sortie au Musée des sciences est confirmée pour le "
             f"{random_day_month()}. Veuillez rapporter la permission signée au "
             f"secrétariat avant {random_day()}.\n\nMme Lavoie",
     "Sortie au Musée des sciences"),
    (lambda: "Menu de la cafétéria de mardi : poutine, salade du jardin et "
             "compote de pommes. Bon appétit !\n\nLe service de cafétéria",
     "Menu de la semaine"),
    (lambda: "Le tournoi de soccer interclasses aura lieu la semaine "
             "prochaine. Les inscriptions se font au secrétariat jusqu'à "
             "jeudi.\n\nM. Gagnon",
     "Tournoi de soccer"),
    (lambda: "Rencontre du club de robotique jeudi à 12 h au local C-204. "
             "Apportez votre ordinateur portable.\n\nMme Bélanger",
     "Club de robotique"),
    (lambda: "Les parents sont invités à la soirée portes ouvertes le 22 "
             "avril à 18 h. Une garderie sera disponible sur place.\n\n"
             "La direction",
     "Soirée portes ouvertes"),
    (lambda: "Séance de récupération en mathématiques : jeudi à 12 h au local "
             "B-108. Aucune inscription requise.\n\nM. Bergeron",
     "Récupération en mathématiques"),
    (lambda: "Répétition de la chorale mercredi à 15 h 30 à l'auditorium. "
             "Présence obligatoire pour le spectacle de fin d'année.\n\n"
             "Mme Girard",
     "Répétition de la chorale"),
    (lambda: "Le club de bénévolat cherche des élèves pour la bibliothèque "
             "municipale, les mardis après l'école. Inscription au local "
             "D-112.\n\nMme Morin",
     "Club de bénévolat"),
    (lambda: "Vendredi, c'est la journée pyjama pour le carnaval d'hiver ! "
             "Apportez 2 $ pour la fondation de l'école.\n\nLe comité étudiant",
     "Journée pyjama"),
    (lambda: "Les bulletins seront disponibles sur le portail des parents "
             "lundi après-midi.\n\nLe secrétariat",
     "Publication des bulletins"),
    (lambda: "Petit changement : l'autobus 3 partira de la rue des Érables à "
             "partir de lundi.\n\nLe transport scolaire",
     "Changement d'itinéraire"),
    (lambda: "La trousse d'urgence de l'école doit être complétée avec des "
             "gants et une bouteille d'eau. Merci de votre collaboration.\n\n"
             "La direction",
     "Trousse d'urgence"),
]

for _ in range(6):
    for build, subject in HAM_ADMIN:
        add(f"direction@{SCHOOL_DOMAIN}", "École secondaire", subject,
                build(), return_path=f"direction@{SCHOOL_DOMAIN}")

HAM_PERSONAL = [
    (lambda: f"Salut ! Tu viens jouer au hockey dehors samedi après-midi ? "
             f"On se rejoint au parc des Hirondelles à 13 h.\n\n{random.choice(FIRST_NAMES_M)}",
     "Hockey samedi ?"),
    (lambda: f"Allô ! Pour le devoir d'anglais, je me suis perdue à la "
             f"question 4. On se voit à la bibliothèque demain midi ?\n\n{random.choice(FIRST_NAMES_F)}",
     "Question sur le devoir"),
    (lambda: "Bonjour mon trésor, tu viens souper dimanche ? Je fais ton "
             "gâteau aux carottes préféré !\n\nGrand-maman",
     "Souper de dimanche"),
    (lambda: f"Salut ! Mon cousin m'a prêté un nouveau jeu. On joue en ligne "
             f"vendredi soir après tes devoirs ?\n\n{random.choice(FIRST_NAMES_M)}",
     "Partie en ligne vendredi"),
    (lambda: f"Coucou ! Pour le projet de sciences, j'ai trouvé un site avec "
             f"plein d'informations sur les volcans. Je te l'envoie demain.\n\n{random.choice(FIRST_NAMES_F)}",
     "Pour le projet de sciences"),
    (lambda: "Salut ! L'équipe de soccer s'entraîne samedi à 9 h au terrain "
             "du parc. N'oublie pas ton chandail rouge.\n\nCoach Martin",
     "Entraînement samedi"),
    (lambda: f"Allô ! Ma fête de fin de session est samedi à 14 h chez moi. "
             f"Tu peux confirmer ta présence ?\n\n{random.choice(FIRST_NAMES_F)}",
     "Invitation à ma fête"),
    (lambda: "Salut ! Peux-tu m'attendre après le cours de sciences ? On doit "
             "ramasser des fournitures au magasin pour le projet.\n\nThomas",
     "Fournitures pour le projet"),
    (lambda: "Allô ! Si le temps est beau dimanche, on fait une excursion à "
             "vélo le long de la rivière. Tu es partant ?\n\nWilliam",
     "Excursion à vélo"),
    (lambda: "Bonjour mon grand, j'ai des photos de notre voyage à te "
             "montrer. Viens me voir après l'école.\n\nMarraine Lucie",
     "Photos du voyage"),
    (lambda: "Salut ! Pour le camping, voici ma liste : tente, sac de "
             "couchage, lampe de poche et barres tendres. À samedi !\n\nAntoine",
     "Liste pour le camping"),
    (lambda: f"Salut ! As-tu mon cahier de sciences ? Je pense l'avoir "
             f"oublié au local B-204. Merci !\n\n{random.choice(FIRST_NAMES_F)}",
     "Cahier oublié"),
    (lambda: "Bonjour, la saison de soccer commence le 15 mai. Les uniformes "
             "seront distribués lundi.\n\nLe comité des sports",
     "Début de saison"),
    (lambda: "Chers membres, le club de lecture se réunit jeudi à 12 h. "
             "Nouveau livre : « Les ailes de Léa ».\n\nLe club de lecture",
     "Club de lecture"),
    (lambda: "Bonjour, votre abonnement au journal de l'école : premier "
             "numéro vendredi. Confirmez votre adresse.\n\nLe journal étudiant",
     "Journal de l'école"),
    (lambda: "Bonjour ! La partie de cartes de vendredi est déplacée chez "
             "William. Apporte tes chips préférés !\n\nÉdouard",
     "Partie de cartes vendredi"),
]

for _ in range(4):
    for build, subject in HAM_PERSONAL:
        first_name = random.choice(FIRST_NAMES_F + FIRST_NAMES_M)
        last_name = random.choice(LAST_NAMES)
        add(f"{first_name.lower()}.{last_name.lower()}@{SCHOOL_DOMAIN}",
                f"{first_name} {last_name}", subject, build())

HAM_TEACHER = [
    (lambda: f"Bonjour, vos résultats de l'examen de {random_subject()} sont "
             f"corrigés. Vous avez bien travaillé, continuez ainsi !\n\n{random_teacher()}",
     "Résultats de l'examen"),
    (lambda: f"Bonjour, une petite question sur le devoir de {random_subject()} : au "
             f"numéro 2, on doit souligner les verbes ou les adjectifs ? "
             f"Merci !\n\n{random.choice(FIRST_NAMES_F)} {random.choice(LAST_NAMES)}",
     "Question sur le devoir"),
    (lambda: "Rappel : le projet de sciences est à remettre vendredi avant "
             "16 h. N'oubliez pas votre carnet de laboratoire.\n\nM. Gagnon",
     "Projet à remettre"),
    (lambda: "Avis aux élèves du cours de chimie : portez votre sarrau et "
             "vos lunettes pour la séance de laboratoire de jeudi.\n\n"
             "Mme Lavoie",
     "Laboratoire de chimie"),
    (lambda: "Lecture à faire pour lundi : le chapitre 4 du roman « La forêt "
             "mystérieuse ». Un petit quiz vous attend !\n\nM. Roy",
     "Lecture pour lundi"),
    (lambda: "Changement d'horaire : l'examen d'histoire est devancé à "
             "mercredi au lieu de jeudi. Bonne révision !\n\nMme Bélanger",
     "Examen devancé"),
    (lambda: "Bonjour, les résultats du quiz d'histoire sont affichés sur le "
             "portail. On reprendra le chapitre 2 en classe.\n\nMme Bélanger",
     "Résultats du quiz"),
    (lambda: "Atelier optionnel de programmation : samedi matin au local "
             "d'informatique. Maximum 15 places.\n\nM. Caron",
     "Atelier de programmation"),
    (lambda: "Exercices de révision avant l'examen : pages 18 à 25 du "
             "cahier. Les réponses seront corrigées en classe vendredi.\n\n"
             "M. Bergeron",
     "Révision avant l'examen"),
    (lambda: "Le concours de mathématiques du district aura lieu le 12 mai. "
             "Les élèves intéressés doivent me le dire avant vendredi.\n\n"
             "M. Bergeron",
     "Concours de mathématiques"),
]

for _ in range(5):
    for build, subject in HAM_TEACHER:
        add(f"prof.{random.choice(LAST_NAMES).lower()}@{SCHOOL_DOMAIN}", random_teacher(), subject,
                build(), return_path=f"prof.{random.choice(LAST_NAMES).lower()}@{SCHOOL_DOMAIN}")

HAM_BRAND = [
    ("comptes@hydroquebec.com", "Hydro-Québec",
     "Votre facture de février est disponible",
     ("Votre facture est accessible dans votre Espace client. Montant : "
     "87,43 $. Aucune action requise si vous êtes inscrit au prélèvement "
     "automatique.\n\nHydro-Québec"),
     "comptes@hydroquebec.com"),
    ("noreply@desjardins.com", "AccèsD Desjardins",
     "Transaction sur votre compte",
     ("Bonjour, une transaction a été effectuée sur votre compte AccèsD. "
     "Consultez vos relevés sur accesd.desjardins.com pour les détails.\n\n"
     "Desjardins"),
     "noreply@desjardins.com"),
    ("noreply@steampowered.com", "Steam",
     "Confirmation de votre achat",
     ("Bonjour, votre achat de la semaine est confirmé. Le téléchargement du "
     "jeu est disponible dans votre bibliothèque Steam.\n\nL'équipe Steam"),
     "noreply@steampowered.com"),
    ("info@netflix.com", "Netflix",
     "Votre abonnement est renouvelé",
     ("Bonjour, nous vous confirmons le renouvellement de votre abonnement "
     "Netflix. Aucune action requise. Merci !\n\nNetflix"),
     "info@netflix.com"),
    ("receipts@apple.com", "Apple",
     "Reçu de l'App Store",
     ("Bonjour, voici votre reçu de l'App Store pour l'application de "
     "mathématiques. Montant : 4,99 $.\n\nApple"),
     "receipts@apple.com"),
    ("comptes@bmo.com", "BMO",
     "Confirmation de virement",
     ("Bonjour, votre virement de 25 $ a été effectué avec succès. Un accusé "
     "vous a été envoyé par courriel.\n\nBMO"),
     "comptes@bmo.com"),
    ("commande@amazon.ca", "Amazon.ca",
     "Votre commande est expédiée",
     ("Bonjour, votre commande est expédiée ! Vous pouvez suivre le colis sur "
     "amazon.ca avec le numéro 1Z-8821-4471.\n\nAmazon.ca"),
     "commande@amazon.ca"),
    ("noreply@microsoftonline.com", "Équipe Microsoft 365",
     "Votre mot de passe expirera bientôt",
     ("Bonjour, votre mot de passe Microsoft expirera dans 30 jours. "
     "Mettez-le à jour sur outlook.live.com lorsque vous aurez le temps.\n\n"
     "Microsoft"),
     "noreply@microsoftonline.com"),
]

for _ in range(5):
    for entry in HAM_BRAND:
        sender, name, subject, body, return_path = entry
        add(sender, name, subject, body, return_path=return_path)

HAM_NEWSLETTER = [
    ("info@infolettre-cuisine.com", "Infolettre Cuisine",
     "Infolettre - 5 recettes de saison",
     ("Voici notre infolettre de la semaine : 5 recettes de saison avec des "
     "légumes du Québec. Pour vous désabonner, utilisez le lien en bas de "
     "page.\n\nL'équipe Cuisine du coin")),
    ("info@bibliotheque-municipale.qc.ca", "La bibliothèque",
     "Nouveautés de la bibliothèque",
     ("Nouveautés : 12 nouvelles bandes dessinées et 8 romans jeunesse sont "
     "arrivés. Bonne lecture !\n\nLa bibliothèque")),
    ("info@sports-quartier.qc.ca", "Le comité des sports",
     "Bulletin des sports du quartier",
     ("Le bulletin des sports du quartier : inscriptions au camp de soccer, "
     "match de hockey samedi et résultats de la ligue.\n\nLe comité des sports")),
    ("journal@dessources.qc.ca", "Le journal de l'école",
     "Le journal de l'école est arrivé",
     ("Le journal de l'école vous salue ! Ce mois-ci : l'entrevue avec la "
     "gagnante du concours de poésie et les photos de la journée carnaval.\n\n"
     "Le comité du journal")),
    ("info@ecoaction.qc.ca", "EcoAction",
     "Infolettre de l'environnement",
     ("L'infolettre de l'environnement : le grand ménage de printemps du parc "
     "est samedi. Des gants seront fournis.\n\nEcoAction")),
    ("club@echecs-ecole.qc.ca", "Le club d'échecs",
     "Tournoi interne dimanche",
     ("Le club d'échecs publie son infolettre : tournoi interne dimanche à "
     "13 h, niveau débutant bienvenu.\n\nLe club d'échecs")),
    ("coop@dessources.qc.ca", "La coop scolaire",
     "Fruits et légumes de la semaine",
     ("La coop scolaire a reçu ses fruits et légumes de la semaine : pommes, "
     "bananes et carottes. Passez nous voir !\n\nLa coop")),
]

for _ in range(5):
    for sender, name, subject, body in HAM_NEWSLETTER:
        add(sender, name, subject, body,
                return_path=f"bounce-{random.randint(1000, 9999)}@{sender.split('@')[1]}")

HAM_TRANSACTION = [
    ("info@librairie-du-quartier.ca", "Librairie du quartier",
     "Confirmation de votre commande",
     ("Bonjour, merci pour votre commande ! Elle sera livrée le 5 mars entre "
     "9 h et 17 h. Bonne lecture !\n\nLibrairie du quartier")),
    ("boutique@dessources.qc.ca", "La boutique étudiante",
     "Reçu de votre achat",
     ("Voici le reçu de votre achat à la boutique du cours "
     "d'entrepreneuriat : 2 marque-pages et 1 chandail. Merci de votre "
     "soutien !\n\nLa boutique étudiante")),
    ("inscription@camp-hirondelles.ca", "Le camp des Hirondelles",
     "Votre inscription est confirmée",
     ("Votre inscription au camp de jour est confirmée pour la semaine du "
     "6 juillet. Le paiement de 120 $ est reçu.\n\nLe camp des Hirondelles")),
    ("journal@dessources.qc.ca", "Le journal étudiant",
     "Abonnement renouvelé",
     ("Votre abonnement au journal étudiant est renouvelé jusqu'en juin. Le "
     "premier numéro arrive vendredi.\n\nLe journal étudiant")),
    ("secretaire@dessources.qc.ca", "Le secrétariat",
     "Réservation de local confirmée",
     ("Réservation confirmée : le local A-215 est réservé pour votre "
     "présentation de mercredi à 13 h.\n\nLe secrétariat")),
]

for _ in range(5):
    for sender, name, subject, body in HAM_TRANSACTION:
        add(sender, name, subject, body,
                return_path=f"bounce-{random.randint(1000, 9999)}@{sender.split('@')[1]}")

# HAM — traps: legit emails that trigger rules
HAM_TRAP = [
    ("info@infolettre-cuisine.com", "Infolettre Cuisine",
     "Votre renouvellement",
     ("Bonjour, profitez de 20 % de rabais sur votre renouvellement "
     "d'abonnement à notre infolettre de recettes — vous êtes membre depuis "
     "2019 ! Merci de votre fidélité.\n\nCuisine du coin")),
    ("coop@dessources.qc.ca", "La coop scolaire",
     "Rapport trimestriel",
     ("Rapport trimestriel de la coop scolaire : croissance de 12 % des "
     "ventes de pommes et de grignotines. Merci aux bénévoles !\n\nLa coop")),
    ("secretaire@dessources.qc.ca", "Le secrétariat",
     "ATTENTION : changement de local",
     ("ATTENTION : changement de local pour le cours d'anglais de jeudi. Le "
     "nouveau local est le B-302.\n\nLe secrétariat")),
    ("mme.fortin@dessources.qc.ca", "Mme Fortin",
     "URGENT : RE: TP3",
     ("URGENT : RE: TP3 — la date limite de remise est reportée au 14 mars. "
     "Merci !\n\nMme Fortin")),
    ("m.roy@dessources.qc.ca", "M. Roy",
     "Victoire au volleyball !",
     ("Félicitations à l'équipe gagnante du tournoi de volleyball !!! Trois "
     "belles victoires en finale. On est fiers de vous !\n\nM. Roy")),
    ("comite@dessources.qc.ca", "Le comité étudiant",
     "Concours de poésie",
     ("Bonjour, le concours de poésie de l'école offre la chance de gagner "
     "des livres. La remise des prix aura lieu au gala de fin d'année.\n\n"
     "Le comité étudiant")),
    ("m.caron@dessources.qc.ca", "M. Caron",
     "Liens pour vos travaux",
     ("Voici les liens pour vos travaux : https://www.apple.com/ca/fr/support "
     "pour le tutoriel, https://outlook.live.com/mail/ pour votre boîte et "
     "https://www.postescanada.ca/suivi pour suivre votre envoi. Bonne "
     "chance !\n\nM. Caron")),
    ("bibliotheque@dessources.qc.ca", "La bibliothèque",
     "Entrée gratuite au musée",
     ("GRATUIT pour les membres : l'entrée au musée des sciences est offerte "
     "avec votre carte de la bibliothèque cette fin de semaine.\n\n"
     "La bibliothèque")),
]

for _ in range(5):
    for sender, name, subject, body in HAM_TRAP:
        add(sender, name, subject, body)

HAM_SHORT = [
    ("secretaire@dessources.qc.ca", "Le secrétariat",
     "ATTENTION",
     "ATTENTION : changement de local pour vendredi. Voir la liste au tableau.\n\nLe secrétariat"),
    ("mme.fortin@dessources.qc.ca", "Mme Fortin",
     "URGENT : RE: TP3",
     "URGENT : RE: TP3 — reporté au 14 mars.\n\nMme Fortin"),
    ("m.roy@dessources.qc.ca", "M. Roy",
     "RAPPEL",
     "RAPPEL : pratique de soccer annulée ce soir.\n\nM. Roy"),
    ("secretaire@dessources.qc.ca", "La cafétéria",
     "INFO",
     "INFO : la cafétéria ferme à 13 h vendredi.\n\nLa cafétéria"),
    ("direction@dessources.qc.ca", "La direction",
     "CHANGEMENT",
     "CHANGEMENT : l'examen est déplacé à lundi.\n\nLa direction"),
]

for _ in range(2):
    for sender, name, subject, body in HAM_SHORT:
        add(sender, name, subject, body)

HAM_LINKS = [
    ("noreply@desjardins.com", "AccèsD Desjardins",
     "Accès à vos relevés",
     ("Bonjour, pour consulter vos relevés, connectez-vous sur "
     "https://accesd.desjardins.com/identification. Merci !\n\nDesjardins")),
    ("info@netflix.com", "Netflix",
     "Catalogue de la semaine",
     ("Bonjour, votre sélection de la semaine vous attend sur "
     "https://www.netflix.com/browse. Bonne écoute !\n\nNetflix")),
    ("support@apple.com", "Apple",
     "Aide et support",
     ("Bonjour, notre page d'aide est disponible au "
     "https://www.apple.com/ca/fr/support. N'hésitez pas à la consulter.\n\n"
     "Apple")),
    ("suivi@postescanada.ca", "Postes Canada",
     "Suivi de votre envoi",
     ("Bonjour, vous pouvez suivre votre envoi au "
     "https://www.postescanada.ca/suivi. Le colis avance bien.\n\n"
     "Postes Canada")),
    ("noreply@steampowered.com", "Steam",
     "Nouveautés de la semaine",
     ("Bonjour, les nouveautés sont dans votre bibliothèque : "
     "https://steamcommunity.com/market. Bonne découverte !\n\nSteam")),
    ("comptes@amazon.ca", "Amazon.ca",
     "Vos commandes",
     ("Bonjour, retrouvez l'historique de vos commandes au "
     "https://www.amazon.ca/gp/orders. Merci !\n\nAmazon.ca")),
    ("info@revenuquebec.ca", "Revenu Québec",
     "Services en ligne",
     ("Bonjour, les services en ligne sont accessibles au "
     "https://www.revenuquebec.ca/citoyens. Bonne journée !\n\nRevenu Québec")),
    ("noreply@microsoftonline.com", "Microsoft 365",
     "Votre boîte de courriel",
     ("Bonjour, accédez à votre boîte au https://outlook.live.com/mail/ "
     "pour lire vos messages.\n\nMicrosoft 365")),
]

for _ in range(5):
    for sender, name, subject, body in HAM_LINKS:
        add(sender, name, subject, body)

SPAM_PRIZE = [
    ("promo@concours-gratuit.top", "Concours Gratuit",
     "FÉLICITATIONS !!! VOUS AVEZ GAGNÉ UN IPHONE GRATUIT !",
     ("FÉLICITATIONS !!! VOUS AVEZ GAGNÉ UN IPHONE GRATUIT ! Pour réclamer "
     "votre prix, cliquez sur le lien ci-dessous dans les 24 heures.\n\n"
     "http://concours-gratuit.top/iphone\n\nCe concours est réservé aux "
     "participants chanceux.")),
    ("tirage@offres-express.info", "Tirage Express",
     "Gagnez une carte cadeau de 100 $ chez Amazon !",
     ("Gagnez une carte cadeau de 100 $ chez Amazon ! Participez à notre "
     "tirage en répondant à ce courriel avant minuit.\n\nhttp://bit.ly/3xK9pQ")),
    ("voyages@voyages-etoiles.top", "Voyages Étoiles",
     "VOUS AVEZ ÉTÉ SÉLECTIONNÉ POUR UN VOYAGE GRATUIT AUX CARAÏBES !",
     ("VOUS AVEZ ÉTÉ SÉLECTIONNÉ POUR UN VOYAGE GRATUIT AUX CARAÏBES ! "
     "Répondez à ce courriel pour réclamer votre prix.\n\nL'équipe Voyages "
     "Étoiles")),
    ("promo@tirage-magique.info", "Tirage Magique",
     "Concours : gagnez un abonnement Netflix pour un an !",
     ("Concours : gagnez un abonnement Netflix pour un an ! C'est gratuit et "
     "facile. Cliquez ici pour participer.\n\nhttp://tirage-magique.info")),
    ("concours@console-chance.xyz", "Console Chance",
     "Participez au tirage d'une console de jeux !",
     ("Participez au tirage d'une console de jeux ! Un gagnant par semaine. "
     "La participation est gratuite.\n\nhttps://tinyurl.com/xk991")),
    ("cinema@cinema-plus.info", "Cinéma Plus",
     "GAGNEZ DES BILLETS DE CINÉMA !!!",
     ("GAGNEZ DES BILLETS DE CINÉMA !!! Répondez en 24 heures pour avoir une "
     "chance de gagner un laissez-passer pour deux.\n\nL'équipe Cinéma Plus")),
    ("offre@offre-express.top", "Offre Express",
     "Carte cadeau de 50 $ pour les 100 premiers participants !",
     ("Offre spéciale : carte cadeau de 50 $ pour les 100 premiers "
     "participants ! Cliquez vite avant que ce soit trop tard.\n\n"
     "http://offre-express.top")),
    ("webmaster@bonus-fantastique.tk", "Bonus Fantastique",
     "Vous êtes le 1 000 000e visiteur !",
     ("Vous êtes le 1 000 000e visiteur de notre site ! Cliquez sur le lien "
     "pour réclamer votre prix gratuit.\n\nhttp://bonus-fantastique.tk")),
    ("rentree@rentree-chance.xyz", "Rentrée Chance",
     "Tirage de rentrée : gagnez une tablette gratuite !",
     ("Tirage de rentrée : gagnez une tablette gratuite ! Inscrivez-vous "
     "avant le 31 août.\n\nhttp://rentree-chance.xyz")),
    ("sport@sport-chance.info", "Sport Chance",
     "Gagnez le chandail de votre équipe préférée !",
     ("Gagnez le chandail de votre équipe préférée ! Concours gratuit pour "
     "tous les abonnés.\n\nhttps://bit.ly/2w8YbZ")),
]

for _ in range(6):
    for sender, name, subject, body in SPAM_PRIZE:
        add(sender, name, subject, body, label="spam")

SPAM_DISCOUNT = [
    ("soldes@magasin-promo.info", "Magasin Promo",
     "MÉGA SOLDES : 70 % de rabais sur tout !",
     ("MÉGA SOLDES : 70 % de rabais sur tout le magasin ! Seulement cette fin "
     "de semaine. Achetez maintenant.\n\nhttp://magasin-promo.info")),
    ("solde@vetements-solde.top", "Vêtements Solde",
     "SOLDE DE FIN DE SAISON : jusqu'à 50 % de rabais",
     ("SOLDE DE FIN DE SAISON : jusqu'à 50 % de rabais sur les vêtements. Les "
     "quantités sont limitées.\n\nhttp://vetements-solde.top")),
    ("jeux@jeux-offre.xyz", "Jeux Offre",
     "Offre de lancement : -30 % sur les nouveaux jeux !",
     ("Offre de lancement : -30 % sur les nouveaux jeux vidéo cette semaine "
     "seulement !\n\nhttp://jeux-offre.xyz")),
    ("cinema@cinema-2pour1.info", "Cinéma Deux pour Un",
     "PROMOTION EXCLUSIVE : deux billets pour le prix d'un !",
     ("PROMOTION EXCLUSIVE : deux billets pour le prix d'un au cinéma du "
     "quartier !\n\nhttp://cinema-2pour1.info")),
    ("rabais@librairies-rabais.top", "Librairies Rabais",
     "Rabais étudiants : 20 % de rabais en librairie",
     ("Rabais étudiants : 20 % de rabais dans toutes les librairies "
     "participantes. Montrez votre carte d'étudiant !\n\n"
     "http://librairies-rabais.top")),
    ("vente@liquidation-vite.info", "Liquidation Vite",
     "SOLDES DE LIQUIDATION : tout à moitié prix !",
     ("SOLDES DE LIQUIDATION : tout à moitié prix pendant 48 heures "
     "seulement ! Ne manquez pas ça.\n\nhttp://liquidation-vite.info")),
    ("premier@premiers-achats.tk", "Premiers Achats",
     "Prix réduit de 40 % pour les 100 premiers achats !",
     ("Prix réduit de 40 % pour les 100 premiers achats de la semaine ! "
     "Commandez maintenant.\n\nhttp://premiers-achats.tk")),
    ("smoothie@smoothies-offre.xyz", "Smoothies Offre",
     "2 pour 1 sur les smoothies cette semaine !",
     ("2 pour 1 sur les smoothies cette semaine seulement ! Offre valable en "
     "magasin et en ligne.\n\nhttp://smoothies-offre.xyz")),
    ("musique@musique-rabais.info", "Musique Rabais",
     "Économisez 25 % sur votre abonnement musical",
     ("Économisez 25 % sur votre prochain abonnement musical. Une offre "
     "limitée pour les nouveaux membres.\n\nhttp://musique-rabais.info")),
    ("pizza@pizza-special.top", "Pizza Spécial",
     "Pizza à 10 $ au lieu de 15 $ !",
     ("Pizza à 10 $ au lieu de 15 $ : l'offre de la semaine chez votre "
     "livreur préféré. Commandez avant dimanche !\n\nhttp://pizza-special.top")),
]

for _ in range(6):
    for sender, name, subject, body in SPAM_DISCOUNT:
        add(sender, name, subject, body, label="spam")

# SPAM — promo phrasing
SPAM_PROMO = [
    ("promo@boutique-lumineuse.xyz", "Boutique Lumineuse",
     "Achetez maintenant, les stocks sont limités !",
     ("Achetez maintenant, les stocks sont limités ! Les nouveautés se "
     "vendent vite.\n\nhttp://boutique-lumineuse.xyz")),
    ("offre@occasion-vite.info", "Occasion Vite",
     "Offre limitée — expire dans 24 heures !",
     ("Offre limitée — expire dans 24 heures ! Ne laissez pas passer cette "
     "occasion.\n\nhttp://occasion-vite.info")),
    ("games@games-deal.top", "Games Deal",
     "BUY NOW and save 70 % on all games !",
     ("BUY NOW and save 70 % on all games ! This week only.\n\n"
     "http://games-deal.top")),
    ("livraison@livraison-gratuite.info", "Livraison Gratuite",
     "Commandez avant minuit pour la livraison gratuite",
     ("Commandez avant minuit pour la livraison gratuite. Dépêchez-vous, "
     "l'horloge tourne !\n\nhttp://livraison-gratuite.info")),
    ("vedette@articles-vedettes.tk", "Articles Vedettes",
     "Dernière chance : quantités limitées !",
     ("Dernière chance : quantités limitées sur les articles vedettes. Une "
     "fois partis, c'est fini.\n\nhttp://articles-vedettes.tk")),
    ("soir@offre-soir.xyz", "Offre Soir",
     "Ne manquez pas cette offre — elle se termine ce soir",
     ("Ne manquez pas cette offre — elle se termine ce soir à 23 h 59. "
     "Vraiment !\n\nhttp://offre-soir.xyz")),
    ("deal@deal-special.info", "Deal Spécial",
     "Special deal just for you : -50 % de rabais aujourd'hui",
     ("Special deal just for you : -50 % de rabais aujourd'hui seulement. "
     "C'est votre jour de chance !\n\nhttp://deal-special.info")),
    ("catalogue@catalogue-promo.top", "Catalogue Promo",
     "Prix de lancement : 20 % de réduction sur tout",
     ("Prix de lancement : 20 % de réduction sur tout le catalogue. La promo "
     "dure une seule journée.\n\nhttp://catalogue-promo.top")),
    ("reste@unites-restantes.info", "Unités Restantes",
     "Seulement 3 unités restantes à ce prix !",
     ("Seulement 3 unités restantes à ce prix — réservez vite avant d'être "
     "déçu !\n\nhttp://unites-restantes.info")),
    ("abo@abonnements-offre.xyz", "Abonnements Offre",
     "Offre de la semaine : 30 % de moins sur tous les abonnements",
     ("Offre de la semaine : 30 % de moins sur tous les abonnements. Achetez "
     "maintenant, c'est le bon moment !\n\nhttp://abonnements-offre.xyz")),
]

for _ in range(5):
    for sender, name, subject, body in SPAM_PROMO:
        add(sender, name, subject, body, label="spam")

# SPAM — uppercase & exclamations
SPAM_UPPERCASE = [
    ("offer@super-offer.top", "Super Offer",
     "SUPER OFFER !!!! DONT MISS IT !!!!",
     "SUPER OFFER !!!! DONT MISS IT !!!! Click HERE !!!\n\nhttp://super-offer.top"),
    ("vente@rabais-fou.xyz", "Rabais Fou",
     "OFFRE INCROYABLE !!! -80 % DE RABAIS SUR TOUT !!!",
     ("OFFRE INCROYABLE !!! -80 % DE RABAIS SUR TOUT !!! VENEZ VITE !!!\n\n"
     "http://rabais-fou.xyz")),
    ("promo@mega-vente.info", "Méga Vente",
     "PROFITEZ-EN !!! MÉGA VENTE DE LA SEMAINE !!!",
     ("PROFITEZ-EN !!! MÉGA VENTE DE LA SEMAINE !!! TOUT DOIT "
     "DISPARAÎTRE !!!\n\nhttp://mega-vente.info")),
    ("chance@chance-une.info", "Chance Unique",
     "NE MANQUEZ PAS CETTE CHANCE !!! UNE SEULE JOURNÉE !!!",
     ("NE MANQUEZ PAS CETTE CHANCE !!! UNE SEULE JOURNÉE !!!\n\n"
     "http://chance-une.info")),
    ("appareils@appareils-rabais.top", "Appareils Rabais",
     "ÉCONOMISEZ ÉNORMÉMENT !!! 60 % DE RABAIS !!!",
     ("ÉCONOMISEZ ÉNORMÉMENT !!! 60 % DE RABAIS SUR LES APPAREILS !!!\n\n"
     "http://appareils-rabais.top")),
    ("promo@promo-vite.xyz", "Promo Vite",
     "CLIQUEZ MAINTENANT !!! LA PROMO SE TERMINE BIENTÔT !!!",
     ("CLIQUEZ MAINTENANT !!! LA PROMO SE TERMINE BIENTÔT !!!\n\n"
     "http://promo-vite.xyz")),
    ("echantillon@echantillons-gratuit.tk", "Échantillons Gratuit",
     "GRATUIT !!! GRATUIT !!! GRATUIT !!!",
     ("GRATUIT !!! GRATUIT !!! GRATUIT !!! Des échantillons pour tous !!!\n\n"
     "http://echantillons-gratuit.tk")),
    ("surprise@surprises-quotidiennes.info", "Surprises Quotidiennes",
     "WOW !!! Des surprises chaque jour !!!",
     ("WOW !!! Des surprises chaque jour !!! Inscrivez-vous aujourd'hui !!!\n\n"
     "http://surprises-quotidiennes.info")),
]

for _ in range(5):
    for sender, name, subject, body in SPAM_UPPERCASE:
        add(sender, name, subject, body, label="spam")

# SPAM — multiple links
SPAM_LIENS = [
    ("promo@rabais-multiples.info", "Rabais Multiples",
     "Trois sites, trois rabais !",
     ("Trois sites, trois rabais : http://rabais-un.info, "
     "http://rabais-deux.top et http://rabais-trois.xyz. Visitez-les avant "
     "la fin de la semaine !")),
    ("info@magasin-officiel.info", "Magasin Officiel",
     "Retrouvez-nous partout !",
     ("Retrouvez-nous partout : https://bit.ly/offre1, "
     "https://tinyurl.com/offre2 et http://magasin-officiel.info. Bon "
     "magasinage !")),
    ("vente@prix-choc.info", "Prix Choc",
     "Comparez nos prix !",
     ("Comparez nos prix : http://prix-bas.xyz, http://prix-fous.top et "
     "http://prix-choc.info. Le meilleur prix est chez nous !")),
    ("pages@pages-promo.tk", "Pages Promo",
     "Quatre pages à visiter !",
     ("Nos pages à visiter : http://page1-promo.tk, http://page2-promo.info, "
     "http://page3-promo.xyz et http://page4-promo.top. Quatre chances de "
     "rabais !")),
    ("offre@lien-trois.top", "Lien Trois",
     "L'offre complète est ici !",
     ("L'offre complète est ici : http://lien-un.xyz, http://lien-deux.info "
     "et http://lien-trois.top. C'est votre semaine de chance !")),
]

for _ in range(5):
    for sender, name, subject, body in SPAM_LIENS:
        add(sender, name, subject, body, label="spam")

# SPAM — English
SPAM_ENGLISH = [
    ("money@free-money.top", "Free Money",
     "FREE MONEY NOW — CLICK HERE",
     "FREE MONEY NOW — CLICK HERE to claim your PRIZE !\n\nhttp://free-money.top"),
    ("gift@win-gift.info", "Win Gift",
     "WIN a FREE GIFT — LIMITED TIME",
     "WIN a FREE GIFT — LIMITED TIME, CLICK NOW !!!\n\nhttp://win-gift.info"),
    ("store@exclusive-offer.xyz", "Exclusive Offer",
     "EXCLUSIVE OFFER — 70 % DISCOUNT",
     ("EXCLUSIVE OFFER — 70 % DISCOUNT on all items, BUY NOW !\n\n"
     "http://exclusive-offer.xyz")),
    ("ship@free-shipping.top", "Free Shipping",
     "HURRY ! Only 24 hours left !",
     ("HURRY ! Only 24 hours left ! FREE shipping on everything !\n\n"
     "http://free-shipping.top")),
    ("deal@amazing-deal.info", "Amazing Deal",
     "AMAZING DEAL ! Get 3 for the price of 1 !",
     ("AMAZING DEAL ! Get 3 for the price of 1 ! Order today !\n\n"
     "http://amazing-deal.info")),
    ("stock@limited-stock.tk", "Limited Stock",
     "DON'T WAIT ! LIMITED STOCK !",
     ("DON'T WAIT ! LIMITED STOCK ! Special price for you !\n\n"
     "http://limited-stock.tk")),
]

for _ in range(5):
    for sender, name, subject, body in SPAM_ENGLISH:
        add(sender, name, subject, body, label="spam")

# SPAM — misc
SPAM_MISC = [
    ("cours@anglais-rapide.top", "Anglais Rapide",
     "Apprenez l'anglais en 15 jours !",
     ("Apprenez l'anglais en 15 jours, garanti, sans effort ! Appelez "
     "maintenant au 1-800-555-0199.\n\nhttp://anglais-rapide.top")),
    ("forfait@forfait-super.xyz", "Forfait Super",
     "4 fois plus de données pour le même prix !",
     ("Votre nouveau forfait téléphonique : 4 fois plus de données pour le "
     "même prix ! Offre valable cette semaine.\n\nhttp://forfait-super.xyz")),
    ("musique@musique-1dollar.info", "Musique à 1 $",
     "Votre musique préférée pour 1 $ par mois !",
     ("Écoutez votre musique préférée pour 1 $ par mois pendant 3 mois ! "
     "Nouveaux membres seulement.\n\nhttp://musique-1dollar.info")),
    ("emploi@emploi-simple.top", "Emploi Simple",
     "Emploi d'été : gagnez 20 $ de l'heure !",
     ("Emploi d'été : gagnez 20 $ de l'heure à la maison ! Aucune expérience "
     "requise. Inscrivez-vous vite.\n\nhttp://emploi-simple.top")),
    ("affaires@bonbons-riches.xyz", "Bonbons Riches",
     "Devenez riche en vendant des bonbons !",
     ("Devenez riche en vendant des bonbons ! Notre programme vous montre "
     "comment. Commencez aujourd'hui.\n\nhttp://bonbons-riches.xyz")),
    ("appli@marche-payante.info", "Marche Payante",
     "La nouvelle application qui vous paie pour marcher !",
     ("La nouvelle application qui vous paie pour marcher ! Téléchargez-la "
     "gratuitement.\n\nhttp://marche-payante.info")),
    ("diplome@diplome-express.tk", "Diplôme Express",
     "Obtenez votre diplôme en 15 jours, sans examen !",
     ("Obtenez votre diplôme en 15 jours, sans examen ! Appelez "
     "maintenant.\n\nhttp://diplome-express.tk")),
]

for _ in range(5):
    for sender, name, subject, body in SPAM_MISC:
        add(sender, name, subject, body, label="spam")

# PHISHING — bait-word domains
PHISHING_BAIT = [
    ("securite@desjardins-verification.info", "Service Desjardins",
     "Votre compte a été bloqué",
     ("Bonjour, votre compte Desjardins a été bloqué suite à une activité "
     "inhabituelle. Vérifiez votre identité dès maintenant : "
     "http://desjardins-verification.info\n\nService Desjardins")),
    ("info@netflix-billing.tk", "Netflix",
     "Problème de paiement",
     ("Nous avons détecté une tentative de connexion suspecte sur votre "
     "compte Netflix. Confirmez vos informations de paiement : "
     "http://netflix-billing.tk/update.php\n\nNetflix")),
    ("support@amazon-security-login.com", "Amazon Support",
     "Votre compte Amazon a été suspendu",
     ("Votre compte Amazon a été suspendu. Pour le réactiver, connectez-vous "
     "sur http://amazon-security-login.com\n\nAmazon Support")),
    ("livraison@postes-canada-suivi.info", "Postes Canada",
     "Un colis vous attend",
     ("Un colis vous attend. Veuillez confirmer votre adresse pour la "
     "livraison : http://postes-canada-suivi.info\n\nPostes Canada")),
    ("remboursement@revenu-quebec-remboursement.top", "Revenu Québec",
     "Vous avez droit à un remboursement",
     ("Vous avez droit à un remboursement de 128 $. Cliquez pour le "
     "recevoir : http://revenu-quebec-remboursement.top\n\nRevenu Québec")),
    ("verification@microsoft-account-verify.net", "Microsoft 365",
     "Vérification de votre identifiant",
     ("Votre identifiant Microsoft doit être vérifié avant 48 heures : "
     "http://microsoft-account-verify.net\n\nMicrosoft 365")),
    ("support@apple-id-verify.tk", "Apple Support",
     "Problème de paiement sur votre compte",
     ("Problème de paiement sur votre compte Apple. Régularisez-le ici : "
     "http://apple-id-verify.tk\n\nApple Support")),
    ("service@paypal-verification.info", "PayPal",
     "Votre compte PayPal est limité",
     ("Votre compte PayPal est limité. Retirez la limite en confirmant vos "
     "informations : http://paypal-verification.info\n\nPayPal")),
    ("factures@hydro-quebec-facture.info", "Hydro-Québec",
     "Votre facture est impayée",
     ("Votre facture Hydro-Québec est impayée. Évitez la coupure en payant "
     "ici : http://hydro-quebec-facture.info\n\nHydro-Québec")),
    ("alerte@steam-verification.tk", "Steam Support",
     "Alerte de sécurité sur votre compte",
     ("Alerte de sécurité sur votre compte Steam. Vérifiez votre session : "
     "http://steam-verification.tk\n\nSteam Support")),
]

for _ in range(6):
    for sender, name, subject, body in PHISHING_BAIT:
        add(sender, name, subject, body, label="phishing")

# PHISHING — character substitution
PHISHING_SUBSTITUTION = [
    ("noreply@amaz0n.com", "Amazon",
     "Mise à jour de vos informations",
     ("Bonjour, veuillez mettre à jour vos informations de connexion sur "
     "amaz0n.com pour éviter la suspension de votre compte.\n\nAmazon")),
    ("support@rnicrosoft.com", "Microsoft Support",
     "Connexion depuis un nouvel appareil",
     ("Nous avons remarqué une connexion depuis un nouvel appareil. "
     "Confirmez-la sur rnicrosoft.com.\n\nMicrosoft Support")),
    ("service@paypa1.com", "PayPal",
     "Votre session a expiré",
     ("Votre session paypa1.com a expiré. Connectez-vous pour continuer vos "
     "achats.\n\nPayPal")),
    ("equipe@micr0soft.com", "Équipe Microsoft",
     "Confirmation de votre courriel",
     ("Confirmez votre courriel sur micr0soft.com pour garder l'accès à "
     "votre boîte.\n\nÉquipe Microsoft")),
    ("info@netf1ix.com", "Netflix",
     "Renouvellement de votre abonnement",
     ("Votre abonnement se renouvelle automatiquement. Gérez-le sur "
     "netf1ix.com.\n\nNetflix")),
    ("accesd@desjard1ns.com", "Service Desjardins",
     "Frais inhabituels détectés",
     ("Des frais inhabituels ont été détectés. Vérifiez vos relevés sur "
     "accesd.desjard1ns.com.\n\nService Desjardins")),
    ("securite@st3am.com", "Steam",
     "Votre compte de jeu est à risque",
     "Votre compte de jeu est à risque. Protégez-le sur st3am.com.\n\nSteam"),
    ("alertes@app1e.com", "Apple",
     "Achat non reconnu",
     ("Un achat de 49,99 $ a été effectué. Ce n'est pas vous ? Signalez-le "
     "sur app1e.com.\n\nApple")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_SUBSTITUTION:
        add(sender, name, subject, body, label="phishing")

# PHISHING — domain-end trap
PHISHING_DOMAIN_END = [
    ("securite@desjardins.com.securite-client.xyz", "Service Desjardins",
     "Votre accès sera fermé",
     ("Votre accès sera fermé si vous ne répondez pas : "
     "http://desjardins.com.securite-client.xyz\n\nService Desjardins")),
    ("support@amazon.com.verify-login.top", "Amazon",
     "Réactivez votre compte",
     "Réactivez votre compte : http://amazon.com.verify-login.top\n\nAmazon"),
    ("comptes@netflix.com.account-update.info", "Netflix",
     "Votre paiement est en attente",
     ("Votre paiement est en attente : http://netflix.com.account-update.info\n\n"
     "Netflix")),
    ("verification@microsoft.com.connexion-securisee.xyz", "Microsoft 365",
     "Vérification requise",
     ("Vérification requise : http://microsoft.com.connexion-securisee.xyz\n\n"
     "Microsoft 365")),
    ("suivi@postescanada.ca.suivi-livraison.info", "Postes Canada",
     "Votre colis ne peut pas être livré",
     ("Votre colis ne peut pas être livré : "
     "http://postescanada.ca.suivi-livraison.info\n\nPostes Canada")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_DOMAIN_END:
        add(sender, name, subject, body, label="phishing")

# PHISHING — links: IP, shorteners, HTTP
PHISHING_LINKS = [
    ("securite@desjardins.com", "Service Desjardins",
     "Connexion depuis une adresse inconnue",
     ("Votre compte a été utilisé depuis une adresse inconnue. Vérifiez ici : "
     "http://203.0.113.45/desjardins/login\n\nService Desjardins")),
    ("remboursement@revenuquebec.ca", "Revenu Québec",
     "Récupérez votre remboursement",
     ("Cliquez pour récupérer votre remboursement : https://bit.ly/3xK9pQ\n\n"
     "Revenu Québec")),
    ("service@paypal.com", "PayPal",
     "Sécurisez votre compte",
     ("Suivez votre colis sur ce lien : http://192.0.2.77/paypal/secure\n\n"
     "PayPal")),
    ("support@apple.com", "Apple Support",
     "Mettez à jour vos informations",
     ("Mettez à jour vos informations : http://198.51.100.12/apple/id-verify\n\n"
     "Apple Support")),
    ("verification@microsoft.com", "Microsoft 365",
     "Votre mot de passe expire bientôt",
     ("Votre mot de passe expire bientôt. Renouvelez-le : "
     "http://micr0soft-alert.com/verify\n\nMicrosoft 365")),
    ("livraison@postescanada.ca", "Postes Canada",
     "Confirmez votre adresse de livraison",
     ("Confirmez votre adresse de livraison : "
     "http://postescanada-suivi.info/paiement?ref=8821\n\nPostes Canada")),
    ("comptes@bmo.com", "BMO",
     "Accédez à votre relevé",
     "Accédez à votre relevé : https://tinyurl.com/xk991\n\nBMO"),
    ("support@amazon.ca", "Amazon",
     "Sécurisez votre compte",
     ("Sécurisez votre compte : http://amazon.ca.security-check.xyz/login\n\n"
     "Amazon")),
    ("accesd@desjardins.com", "Desjardins",
     "Votre session a expiré",
     ("Votre session a expiré. Connectez-vous à nouveau : "
     "http://accesd-desjardins-verification.top\n\nDesjardins")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_LINKS:
        add(sender, name, subject, body, label="phishing")

# PHISHING — displayed name vs address
PHISHING_NAME = [
    ("support123@gmail.com", "Amazon Support",
     "Compte bloqué",
     ("Votre compte est bloqué. Cliquez pour le réactiver : "
     "https://bit.ly/3xK9pQ")),
    ("securite@desjardins-verification.info", "Service Desjardins",
     "Vérification de sécurité requise",
     ("Vérification de sécurité requise sur votre compte AccèsD. Agissez "
     "rapidement pour éviter le blocage.")),
    ("support.microsoft.security@gmail.com", "Microsoft Support",
     "Votre session a expiré",
     ("Votre session a expiré. Renouvelez-la pour continuer à utiliser votre "
     "boîte de courriel.")),
    ("info@netflix-billing.tk", "Netflix",
     "Problème de paiement",
     ("Un problème de paiement est survenu sur votre compte. Mettez à jour "
     "votre moyen de paiement ici : http://netflix-billing.tk/update.php")),
    ("livraison@postes-canada-suivi.info", "Postes Canada",
     "Un colis vous attend",
     ("Un colis vous attend au bureau de poste. Confirmez votre adresse pour "
     "la livraison : http://postes-canada-suivi.info")),
    ("service@paypa1.com", "PayPal Service",
     "Compte limité",
     ("Votre compte est limité jusqu'à confirmation de vos informations. "
     "Connectez-vous pour retirer la limite.")),
    ("apple.service.alert@hotmail.com", "Apple Support",
     "Votre identifiant doit être vérifié",
     ("Votre identifiant Apple doit être vérifié avant la fin de la "
     "semaine. Cliquez ici pour continuer : http://apple.id-verify.top/signin")),
    ("factures@hydroquebec-info.xyz", "Hydro-Québec",
     "Facture impayée",
     ("Votre facture est impayée. Évitez les frais en réglant votre solde : "
     "http://hydroquebec-info.xyz/paiement")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_NAME:
        add(sender, name, subject, body, label="phishing")

# PHISHING — Return-Path / Reply-To
PHISHING_HEADERS = [
    ("securite@desjardins.com", "Service Desjardins",
     "Alerte de sécurité sur votre compte",
     ("Alerte de sécurité sur votre compte AccèsD. Veuillez vous connecter "
     "et vérifier vos transactions récentes.\n\nService Desjardins"),
     "<x9921@relais-etranger.info>", ""),
    ("support@microsoft.com", "Microsoft Support",
     "Votre compte a été utilisé",
     ("Votre compte a été utilisé depuis un autre appareil. Consultez votre "
     "historique de connexion.\n\nMicrosoft Support"),
     "<bulk771@ms-alert.info>", "<recovery@mail.com>"),
    ("facturation@fournisseur.ca", "Fournisseur.ca",
     "Confirmation de facturation",
     ("Bonjour, votre facture du mois est prête. Le paiement est dû avant le "
     "30 du mois.\n\nFournisseur.ca"),
     "<facturation@fournisseur.ca>", "<paiements@fournisseur-inv.top>"),
    ("no-reply@netflix.com", "Netflix",
     "Paiement en attente",
     ("Votre paiement est en attente. Mettez à jour votre mode de paiement "
     "pour continuer à regarder.\n\nNetflix"),
     "<bounce-7@netflix-billing.tk>", ""),
    ("noreply@hydroquebec.com", "Hydro-Québec",
     "Remboursement disponible",
     ("Un remboursement est disponible sur votre compte. Communiquez avec "
     "nous pour le recevoir.\n\nHydro-Québec"),
     "<refund@factures-quebec.info>", ""),
    ("info@postescanada.ca", "Postes Canada",
     "Colis en attente de livraison",
     ("Votre colis est en attente de livraison. Confirmez votre adresse "
     "pour finaliser l'envoi.\n\nPostes Canada"),
     "<livraison@suivi-poste.top>", "<livraison@suivi-poste.top>"),
]

for _ in range(5):
    for sender, name, subject, body, return_path, reply_to in PHISHING_HEADERS:
        add(sender, name, subject, body, return_path=return_path,
                reply_to=reply_to, label="phishing")

PHISHING_BAD_DOMAIN = [
    ("securite@desjardins-verification.info", "Desjardins",
     "Connexion à votre compte AccèsD",
     ("Bonjour, nous avons remarqué une connexion à votre compte AccèsD "
     "depuis un appareil que vous ne reconnaissez pas. Pour votre sécurité, "
     "veuillez consulter vos relevés et nous aviser de toute anomalie.\n\n"
     "Merci de votre confiance.")),
    ("noreply@microsoft-account-verify.net", "Microsoft",
     "Votre abonnement Microsoft 365",
     ("Bonjour, votre abonnement Microsoft 365 arrive à échéance. Les "
     "détails de votre facture sont disponibles sur le portail. Bonne "
     "journée.")),
    ("comptes@netflix-billing.tk", "Netflix",
     "Mise à jour de votre facturation",
     ("Bonjour, la facturation de votre compte a été mise à jour. Vous "
     "pouvez consulter le résumé de votre abonnement en tout temps.")),
    ("service@paypa1.com", "PayPal",
     "Votre compte est à jour",
     ("Bonjour, nous vous remercions de votre confiance. Votre compte est à "
     "jour. Pour toute question, communiquez avec nous.")),
    ("no-reply@amaz0n.com", "Amazon",
     "Votre commande a bien été reçue",
     ("Bonjour, votre commande de la semaine a bien été reçue. Un courriel "
     "de confirmation séparé vous sera envoyé. Merci.")),
    ("alerte@bmo-securite.xyz", "BMO",
     "Utilisation de votre carte",
     ("Bonjour, votre carte a été utilisée récemment. Aucune action n'est "
     "requise. Bonne journée.")),
    ("suivi@postescanada-livraison.xyz", "Postes Canada",
     "Envoi en transit",
     ("Bonjour, un envoi est en transit vers votre adresse. Le suivi sera "
     "mis à jour dans les prochaines heures.")),
    ("info@revenu-quebec-verification.info", "Revenu Québec",
     "Votre dossier est en traitement",
     ("Bonjour, votre dossier est en cours de traitement. Les documents "
     "demandés ont bien été reçus. Merci de votre collaboration.")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_BAD_DOMAIN:
        add(sender, name, subject, body, label="phishing")

PHISHING_SCHOOL = [
    ("securite@dessources-verification.xyz", "Portail scolaire",
     "Votre compte sera fermé",
     ("Bonjour, votre compte du portail scolaire sera fermé dans 48 heures "
     "si vous ne confirmez pas votre identité : "
     "http://dessources-verification.xyz/portail")),
    ("noreply@bibliotheque-numerique.tk", "Bibliothèque numérique",
     "Emprunt numérique en retard",
     ("Votre emprunt numérique est en retard. Réinitialisez votre mot de "
     "passe ici : http://bibliotheque-numerique.tk/reinitialiser")),
    ("direction@dessources.qc.ca.connexion.top", "Direction",
     "Mise à jour de vos informations",
     ("Bonjour, la direction vous demande de mettre à jour vos informations "
     "pour la trousse d'urgence : http://dessources.qc.ca.connexion.top")),
    ("helpdesk@dessources-message.info", "Équipe informatique",
     "Votre boîte est presque pleine",
     ("Votre boîte de courriel est presque pleine. Libérez de l'espace ou "
     "agrandissez-la ici : http://dessources-message.info/boite")),
]

for _ in range(5):
    for sender, name, subject, body in PHISHING_SCHOOL:
        add(sender, name, subject, body, label="phishing")


def ensure_unique():
    seen = {}
    for r in ROWS:
        key = (r["sender"], r["name"], r["subject"], r["message"])
        seen.setdefault(key, []).append(r)
    for group in seen.values():
        for i, r in enumerate(group):
            if i == 0:
                continue
            if "@" in r["sender"]:
                local, domain = r["sender"].rsplit("@", 1)
                r["sender"] = f"{local}{random.randint(10, 99)}@{domain}"
            if "@" in r["return_path"]:
                local, domain = r["return_path"].rsplit("@", 1)
                r["return_path"] = f"{local}{random.randint(10, 99)}@{domain}"
            r["message"] += (f"\n\nRéférence : 2026-{random.randint(100, 999)}"
                             f"-{random.randint(1000, 9999)}")


def write():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["sender", "name", "subject", "message",
                           "return_path", "reply_to", "label"])
        writer.writeheader()
        writer.writerows(ROWS)


def summary():
    from collections import Counter
    total = len(ROWS)
    by_label = Counter(r["label"] for r in ROWS)
    with_return_path = sum(1 for r in ROWS if r["return_path"])
    with_reply_to = sum(1 for r in ROWS if r["reply_to"])
    with_link = sum(1 for r in ROWS if "http" in r["message"])
    print(f"Total      : {total}")
    print(f"Labels     : {dict(by_label)}")
    print(f"ReturnPath : {with_return_path}   Reply-To : {with_reply_to}")
    print(f"Avec lien  : {with_link}")
    print(f"Fichier    : {OUTPUT}")


if __name__ == "__main__":
    ensure_unique()
    write()
    summary()
