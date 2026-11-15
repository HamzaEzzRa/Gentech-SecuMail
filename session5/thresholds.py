"""Ici, on règle nos seuils de décision.

Le moteur de scoring transforme les deux scores en verdict
avec ces seuils :

    score_phishing >= SEUIL_PHISHING          ->  PHISHING
    score_phishing >= SEUIL_PHISHING_SUSPECT  ->  SUSPECT
    score_spam     >= SEUIL_SPAM              ->  SPAM
    score_spam     >= SEUIL_SPAM_SUSPECT      ->  SUSPECT
    sinon                                     ->  HAM

Ces valeurs sont un point de départ, pas une réponse.

À la séance 5 :

1. Mesurez vos résultats.
2. Changez une seule valeur.
3. Mesurez encore, et notez l'avant et l'après.

Un seuil choisi au hasard doit être évalué et revu.
"""

SEUIL_PHISHING = 50  # à partir de ce score : PHISHING
SEUIL_PHISHING_SUSPECT = 25  # à partir de ce score : SUSPECT
SEUIL_SPAM = 40  # à partir de ce score : SPAM
SEUIL_SPAM_SUSPECT = 20  # à partir de ce score : SUSPECT
