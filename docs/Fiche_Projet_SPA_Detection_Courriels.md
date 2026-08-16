# FICHE DE PROJET
## Système intelligent de détection de courriels malveillants (spam et hameçonnage)

| | |
|---|---|
| **Programme** | Cybersécurité |
| **Situation-problème** | SP‑A (première des deux) |
| **Mode de travail** | Équipe de 2 à 3 personnes |
| **Durée** | 5 semaines · ≈ 23 h de travail étudiant |
| **Pondération** | À déterminer par l'enseignant |
| **Livrable final** | Prototype fonctionnel + rapport d'analyse + présentation |

---

## 1. Mise en situation

Vous êtes **analystes en cybersécurité junior** au centre des opérations de sécurité (SOC) d'une organisation.

Depuis quelques semaines, les employés signalent une hausse de courriels suspects :

- des messages publicitaires non sollicités (**spam**) ;
- des tentatives de vol d'identifiants (**hameçonnage**) ;
- des courriels qui **imitent des entreprises connues** au moyen de faux domaines et de liens frauduleux.

L'équipe traite les signalements un par un, à la main. Le volume devient ingérable et les analystes n'ont aucun moyen de savoir **par quoi commencer**.

On vous confie le développement d'un **prototype d'analyse automatique** qui examine chaque courriel entrant, lui attribue un **niveau de risque** et permet de prioriser les alertes.

---

## 2. Mandat

Concevoir un moteur d'analyse en deux modules complémentaires, puis le comparer à une approche par apprentissage automatique.

```
                        Courriel reçu
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌───────────────────┐          ┌───────────────────┐
    │  MODULE 1         │          │  MODULE 2         │
    │  Hameçonnage      │          │  Spam             │
    │  Qui écrit ?      │          │  Que dit-on ?     │
    │  identité, domaine│          │  contenu, ton     │
    └─────────┬─────────┘          └─────────┬─────────┘
              │  score_phishing              │  score_spam
              └───────────────┬──────────────┘
                              ▼
                  ┌───────────────────────┐
                  │   MOTEUR DE SCORING   │
                  │  arbitrage + décision │
                  └───────────┬───────────┘
                              ▼
             HAM · SPAM · PHISHING · SUSPECT
                    + niveau de risque
```

**La distinction fondamentale du projet :**

| | Intention | Ce qu'on analyse |
|---|---|---|
| **Spam** | Vous **vendre** quelque chose | Le **contenu** du message |
| **Hameçonnage** | Vous **voler** quelque chose | L'**identité** de l'expéditeur |

C'est pourquoi les deux modules ne regardent pas la même chose. Un hameçonnage bien rédigé ne contient aucun mot suspect ; c'est le domaine qui le trahit.

---

## 3. Phase 1 — Moteur à base de règles (semaines 1 à 3)

### 3.1 Module 1 — Détection d'hameçonnage

L'attaquant exploite le fait que le **nom affiché** est librement modifiable :

```
Nom affiché :   Microsoft Support          ← ce que voit l'utilisateur
Adresse réelle: support.ms.security@gmail.com   ← la vérité
```

Question centrale du module : **l'identité affichée correspond-elle à l'expéditeur réel ?**

| # | Règle | Exemple | Points |
|---|---|---|---|
| 1 | Nom affiché contient une marque connue, mais le domaine ne correspond pas | `Amazon Support` ← `support123@gmail.com` | **+20** |
| 2 | Domaine contenant un mot d'appât (`security`, `login`, `verify`, `support`, `account`, `update`) | `amazon-security-login.com` | **+25** |
| 3 | Domaine ressemblant à un domaine officiel (substitution, ajout, faute) | `amaz0n.com`, `paypa1.com`, `micr0soft.com` | **+30** |
| 4 | Domaine du lien ≠ domaine annoncé dans le texte | texte « Amazon », lien `amazon-login.xyz` | **+25** |
| 5 | Extension de domaine à risque élevé (`.xyz`, `.tk`, `.top`, `.info`…) | `netflix-verify.xyz` | **+10** |
| 6 | *(avancé)* Échec de l'authentification SPF, DKIM ou DMARC | `SPF = FAIL` | **+20** |

> ⚠ **La règle 6 exige les en-têtes complets du courriel.** Elle est impossible à appliquer sur un simple fichier CSV. Elle ne devient réalisable qu'avec des fichiers `.eml`. Traitez-la en option, ou en démonstration.

**Ressource obligatoire à construire :** un fichier `domaines_officiels.csv` associant chaque marque connue à ses domaines légitimes. Sans lui, les règles 1, 3 et 4 sont inapplicables.

```csv
marque,domaines_officiels
amazon,"amazon.ca,amazon.com"
microsoft,"microsoft.com,outlook.com,live.com"
desjardins,"desjardins.com"
```

### 3.2 Module 2 — Détection de spam

| # | Règle | Détection | Points |
|---|---|---|---|
| 1 | Mots-clés commerciaux | `FREE`, `WIN`, `OFFER`, `DISCOUNT`, `SALE`, `MONEY`, `PRIZE`, `GIFT`, `LIMITED`, `CLICK` | **+3** par mot |
| 2 | Excès de majuscules | plus de 40 % des lettres en majuscules | **+10** |
| 3 | Excès de ponctuation | présence de `!!!` ou densité de `!` élevée | **+5** |
| 4 | Formulation promotionnelle | `50% OFF`, `promotion`, `special deal`, `buy now` | **+10** |
| 5 | Nombre de liens élevé | 3 liens ou plus | **+10** |
| 6 | Adresse de retour incohérente | `Return-Path` ≠ `From` | **+10** |

**Vous devez étendre les listes de mots.** Celles ci-dessus sont un point de départ, pas une réponse. Visez au moins 20 termes, en français **et** en anglais, et documentez vos ajouts.

### 3.3 Moteur de scoring — la partie qui décide

Les deux modules produisent chacun un score. Le moteur doit trancher.

**a) Bornage des scores.** La somme brute des règles dépasse 100 (module 1 : jusqu'à 130). Ramenez chaque score dans l'intervalle 0–100, soit en le plafonnant, soit en le normalisant. **Documentez votre choix** : ce n'est pas neutre.

**b) Seuils de décision.** Point de départ à ajuster :

| Score hameçonnage | Score spam | Verdict | Action |
|---|---|---|---|
| ≥ 50 | — | **PHISHING** | Blocage + alerte analyste |
| 25 – 49 | — | **SUSPECT** | Mise en quarantaine, revue humaine |
| < 25 | ≥ 40 | **SPAM** | Dossier « indésirables » |
| < 25 | 20 – 39 | **SUSPECT** | Quarantaine |
| < 25 | < 20 | **HAM** | Livraison normale |

**c) Règle d'arbitrage.** Quand les deux scores sont élevés, **l'hameçonnage l'emporte**. Justification : les conséquences ne sont pas comparables. Une publicité livrée par erreur agace ; un vol d'identifiants non détecté compromet l'organisation.

**d) Niveau de risque** (pour la priorisation dans la file de l'analyste) :

| Score maximal des deux modules | Niveau |
|---|---|
| 0 – 24 | Faible |
| 25 – 49 | Moyen |
| 50 – 74 | Élevé |
| 75 – 100 | Critique |

> **Ces seuils sont provisoires.** Vous devez les **réajuster après avoir mesuré vos résultats** (§5), pas avant. Un seuil choisi au hasard puis jamais revu est une faute de méthode.

### 3.4 Structure des fichiers

```
AntiSpam_Project/
├── main.py                  # point d'entrée, lecture du CSV, affichage
├── phishing_rules.py        # module 1
├── spam_rules.py            # module 2
├── scoring_engine.py        # arbitrage, seuils, niveau de risque
├── evaluation.py            # matrice de confusion et mesures
├── domaines_officiels.csv   # ressource : marques ↔ domaines légitimes
└── donnees/
    ├── emails_test.csv      # jeu de développement (fourni)
    └── corpus/              # jeu réel (phase 2)
```

**Chaque fonction de règle doit renvoyer un couple `(points, explication)`.** Un système de sécurité qui affirme sans justifier est inutilisable en SOC : l'analyste doit pouvoir vérifier.

```python
def regle_domaine_appat(domaine):
    """Renvoie (points, explication)."""
    ...
    return 25, "Domaine contenant le mot d'appât « login »"
```

### 3.5 Format des données

```csv
sender,name,subject,message,label
support123@gmail.com,Amazon Support,Compte bloqué,Veuillez vérifier votre compte,phishing
promo@offres-exemple.biz,Promotion,FREE OFFER,50% discount today,spam
marie.tremblay@cegep-exemple.qc.ca,Marie Tremblay,Remise du TP3,La remise est reportée au 14 mars,ham
```

> La colonne **`label`** est obligatoire : sans elle, aucune évaluation n'est possible. C'est la vérité terrain.

### 3.6 Sortie attendue

```
==================================================
  Email Security Analyzer
==================================================
Expéditeur : Amazon Support <support123@gmail.com>
Sujet      : Compte bloqué

--- Analyse hameçonnage ---
  +20  Marque « amazon » dans le nom, domaine gmail.com non officiel
  +25  Domaine du lien différent du domaine annoncé
  Score : 45/100

--- Analyse spam ---
  +3   Mot-clé « verify »
  Score : 3/100

--- Décision ---
  Verdict        : SUSPECT
  Niveau de risque: Moyen
  Action         : Mise en quarantaine, revue humaine
==================================================
```

---

## 4. Phase 2 — Approche par intelligence artificielle (semaine 4)

Reprendre exactement la même tâche, mais en laissant un modèle **apprendre les règles à partir d'exemples** au lieu de les recevoir de vous.

| Sur quoi | Méthode | Bibliothèque |
|---|---|---|
| Le texte du message | `TfidfVectorizer` + `MultinomialNB` ou `LogisticRegression` | scikit-learn |
| **Vos propres indicateurs** (les points de chaque règle) | `RandomForestClassifier` | scikit-learn |

Le second modèle est le plus intéressant : il voit **exactement les mêmes informations que vos règles**. Seule la manière de les combiner change. `feature_importances_` vous dira quels indicateurs comptent réellement — à confronter aux poids que vous aviez fixés au §3.

**Obligations méthodologiques :**

- séparation entraînement / test **avant** tout entraînement (70/30, stratifiée) ;
- aucune décision de réglage prise en regardant le jeu de test ;
- justification écrite du modèle retenu.

---

## 5. Phase 3 — Mesure et comparaison (semaine 5)

### L'exactitude (*accuracy*) est interdite comme mesure principale

Si 80 % de vos courriels sont légitimes, un système qui répond toujours « HAM » obtient **80 % d'exactitude et ne détecte aucune attaque**. Vous rapportez donc, **par classe** :

- **précision** : parmi ce que j'ai signalé, quelle proportion l'était vraiment ?
- **rappel** : parmi les vraies menaces, quelle proportion ai‑je attrapée ?
- **F1** : l'équilibre entre les deux ;
- la **matrice de confusion** complète.

### Toutes les erreurs ne se valent pas

| Erreur | Conséquence réelle | Gravité |
|---|---|---|
| HAM classé PHISHING | Un courriel de client bloqué, une facture perdue | **La plus grave** |
| PHISHING classé HAM | Vol d'identifiants, compromission | Très grave |
| HAM classé SPAM | Message utile dans les indésirables | Moyenne |
| SPAM classé HAM | Publicité livrée : agaçant | Faible |

Votre rapport doit **chiffrer et commenter** le compromis que vous avez retenu entre ces deux premières erreurs. Il n'existe pas de réglage qui les minimise toutes les deux à la fois : c'est le cœur du métier.

### Tableau comparatif — livrable noté

| Approche | Précision (phishing) | Rappel (phishing) | F1 macro | Faux positifs sur HAM |
|---|---|---|---|---|
| Règles Python | | | | |
| IA — texte | | | | |
| IA — vos indicateurs | | | | |

---

## 6. Questions d'analyse (à traiter dans le rapport)

1. Prenez **trois courriels légitimes** que votre système a signalés à tort. Quelle règle s'est déclenchée ? Que se passerait-il si ce courriel était bloqué dans une vraie entreprise ?
2. Prenez **trois hameçonnages** que votre système a laissés passer. Que leur manquait-il ? Pouviez-vous les attraper sans augmenter vos faux positifs ?
3. Affichez les 20 termes les plus déterminants du modèle texte. Certains n'ont-ils aucun rapport avec la menace (dates, noms de domaines internes, artefacts de format) ? Qu'est-ce que cela révèle ?
4. Vos règles fonctionneraient-elles sur un hameçonnage rédigé **aujourd'hui** ? Et sur un courriel en anglais ? Que faut-il prévoir pour un système déployé ?
5. Votre système attribue un niveau de risque. **Qui est responsable** si un courriel légitime critique est bloqué automatiquement ?

---

## 7. Prérequis Python

| Niveau | Contenu | Nécessaire pour |
|---|---|---|
| Base | variables, listes, dictionnaires, boucles, conditions, fonctions, `try/except` | tout le projet |
| Chaînes et regex | `.lower()`, `.split()`, `.count()`, module `re` | modules 1 et 2 |
| Fichiers | lecture CSV (`csv` ou `pandas`) | données |
| pandas | `read_csv`, filtrage, `value_counts()` | phase 2 |
| scikit-learn | `fit` / `predict`, `train_test_split`, `TfidfVectorizer`, `classification_report` | phases 2 et 3 |

> Environnement recommandé : **Google Colab**. Aucune installation, bibliothèques déjà présentes, partage par lien.

---

## 8. Échéancier

| Semaine | Travail | Jalon |
|---|---|---|
| 1 | Analyse du problème, `domaines_officiels.csv`, squelette du projet | Structure de fichiers fonctionnelle |
| 2 | `phishing_rules.py` et `spam_rules.py` | Les règles renvoient `(points, explication)` |
| 3 | `scoring_engine.py`, seuils, **première mesure** | Matrice de confusion produite |
| 4 | Modèles d'apprentissage, entraînement | Deux modèles entraînés |
| 5 | Comparaison, ajustement des seuils, rapport | Tableau comparatif + rapport |

> **Le jalon de la semaine 3 est le plus important.** Sans mesure chiffrée à ce moment-là, la comparaison de la semaine 5 n'aura aucune valeur : vous n'aurez rien à comparer.

---

## 9. Livrables et évaluation

| Livrable | Pondération |
|---|---|
| Code fonctionnel, structuré et commenté | 25 % |
| Rapport technique (démarche, choix, justifications) | 25 % |
| Tableau comparatif règles vs IA, commenté | 20 % |
| Analyse des erreurs (questions 1 à 3 du §6) | 15 % |
| Présentation orale (10 min) | 15 % |

### Ce qui distingue une bonne note

Entraîner un modèle scikit-learn tient en cinq lignes trouvables en ligne. L'évaluation porte donc sur ce qui **ne se copie pas** :

- la justification de chaque poids et de chaque seuil ;
- le réajustement des seuils **après** mesure, avec preuve du avant/après ;
- l'analyse honnête des erreurs, y compris celles que vous n'avez pas su corriger ;
- la capacité à expliquer une décision du système à quelqu'un qui n'est pas programmeur.

### Balises de réussite

| Niveau | Description |
|---|---|
| Insuffisant | Les règles sont recopiées de la fiche, aucun seuil n'est justifié, l'exactitude sert de mesure |
| Passable | Le système fonctionne, les mesures sont produites mais peu commentées |
| Bien | Règles étendues et justifiées, seuils ajustés après mesure, comparaison correcte |
| Excellent | Analyse fine des faux positifs, compromis assumé et argumenté, limites du système identifiées |

---

## 10. Cadre éthique et légal

- **Aucun courriel réel** d'un camarade, d'un proche ou d'un employeur sans autorisation écrite.
- **Aucun envoi** des courriels de test vers une messagerie active : de vraies personnes recevraient les rebonds.
- **Aucune ouverture** de pièce jointe suspecte, aucune visite des liens analysés.
- Les jeux de données publics servent à l'apprentissage. Ils sont anonymisés et **datés** : ils ne reflètent pas les menaces actuelles.
- Rappel : l'accès non autorisé à un système informatique est une infraction (art. 342.1 du *Code criminel*). La protection des renseignements personnels au Québec relève de la **Loi 25**.

---

## 11. Ressources

**Jeux de données**

| Corpus | Contenu | Accès |
|---|---|---|
| SMS Spam Collection (UCI) | 5 574 messages, ham/spam | `pip install ucimlrepo` → `fetch_ucirepo(id=228)` |
| SpamAssassin Public Corpus | ~9 000 courriels bruts avec en-têtes | `spamassassin.apache.org/old/publiccorpus/` |
| Corpus d'hameçonnage (Nazario, phishing_pot) | courriels d'hameçonnage réels | monkey.org / dépôt GitHub |

**Documentation**

- `re` — expressions régulières : docs.python.org
- scikit-learn — guide de démarrage : scikit-learn.org
- Comprendre SPF, DKIM et DMARC : documentation de votre fournisseur de messagerie
