"""
Modélisation des durées de séjour hospitalier.

Les durées sont simulées à partir de distributions log-normales,
calibrées sur des statistiques hospitalières françaises officielles (DREES).

Sources :
- Hospitalisation complète : durée moyenne 5,5 jours
  DREES — Panorama des établissements de santé 2025
  https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse-documents-de-reference/panoramas-de-la-drees/250522_Panorama_etablissements-de-sante2025

- Soins critiques : durée moyenne 5,2 jours
  DREES — Fiche 13 — Activité et capacités d’accueil en soins critiques (2024)
  https://drees.solidarites-sante.gouv.fr/sites/default/files/2024-07/ES24%20-%20Fiche%2013%20-%20L%E2%80%99activit%C3%A9%20et%20les%20capacit%C3%A9s%20d%E2%80%99accueil%20en%20soins%20critiques.pdf
"""

import math
import random
from enum import Enum


# ============================================================
# Paramètres globaux (jours)
# ============================================================

# Hospitalisation en unité spécialisée
DUREE_MOY_UNITE_J = 5.5
STD_UNITE_J = 2.0  # hypothèse raisonnable (~40%)

# Soins critiques / réanimation
DUREE_MOY_SOINS_CRITIQUES_J = 5.2
STD_SOINS_CRITIQUES_J = 2.6  # variabilité plus forte


# ============================================================
# Types de séjour
# ============================================================

class TypeSejour(Enum):
    UNITE = "UNITE"
    SOINS_CRITIQUES = "SOINS_CRITIQUES"


# ============================================================
# Outils statistiques
# ============================================================

def _tirer_lognormale_jours(moyenne_j: float, std_j: float) -> float:
    """
    Tire une valeur selon une loi log-normale paramétrée à partir d'une moyenne et d'un écart-type (en jours).
    Retourne une durée en jours (float).
    """
    # Sécurité minimale
    if moyenne_j <= 0:
        raise ValueError("La moyenne doit être strictement positive")
    if std_j <= 0:
        raise ValueError("L'écart-type doit être strictement positif")

    sigma2 = math.log(1 + (std_j ** 2) / (moyenne_j ** 2))
    mu = math.log(moyenne_j) - sigma2 / 2
    sigma = math.sqrt(sigma2)

    return random.lognormvariate(mu, sigma)


# ============================================================
# API principale
# ============================================================

def tirer_duree_sejour(type_sejour: TypeSejour) -> int:
    """
    Tire une durée de séjour (en minutes simulées)
    en fonction du type de séjour.

    La durée est tirée UNE SEULE FOIS à l'entrée
    et reste fixe pour le patient.
    """
    if type_sejour == TypeSejour.UNITE:
        jours = _tirer_lognormale_jours(
            DUREE_MOY_UNITE_J,
            STD_UNITE_J,
        )

    elif type_sejour == TypeSejour.SOINS_CRITIQUES:
        jours = _tirer_lognormale_jours(
            DUREE_MOY_SOINS_CRITIQUES_J,
            STD_SOINS_CRITIQUES_J,
        )

    else:
        raise ValueError(f"Type de séjour inconnu : {type_sejour}")

    # Conversion jours → minutes
    return max(1, int(jours * 24 * 60))
