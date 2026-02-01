from core.enums import (
    Localisation,
    EtatPatient,
    Gravite,
    Specialite,
)
from core.patient import Patient
from core.resources import RessourcesService


# ============================================================
# Contraintes sur les salles d'attente
# ============================================================

def peut_entrer_en_salle_attente(
    salle: Localisation,
    ressources: RessourcesService,
) -> bool:
    """
    Vérifie si une salle d'attente dispose d'une capacité disponible.
    Contrainte stricte : capacité maximale non dépassable.
    """
    return (
        salle in ressources.capacites_sa
        and ressources.occupation_sa[salle] < ressources.capacites_sa[salle]
    )


# ============================================================
# Contraintes consultation médicale
# ============================================================

def peut_entrer_en_consultation(
    ressources: RessourcesService,
) -> bool:
    """
    Une consultation nécessite :
    - un médecin disponible
    - aucune double affectation
    """
    return ressources.medecin_disponible


# ============================================================
# Contraintes soins critiques
# ============================================================

def peut_entrer_en_soins_critiques(
    patient: Patient,
) -> bool:
    """
    Règle du modèle :
    - seuls les patients ROUGE peuvent entrer directement
      en soins critiques.
    """
    return patient.gravite == Gravite.ROUGE


# ============================================================
# Contraintes orientation externe
# ============================================================

def doit_etre_oriente_exterieur(
    patient: Patient,
) -> bool:
    """
    Les patients GRIS sont orientés hors du système.
    """
    return patient.gravite == Gravite.GRIS


# ============================================================
# Contraintes hospitalisation / unités aval
# ============================================================

def peut_aller_en_attente_transfert(
    patient: Patient,
) -> bool:
    """
    Contrainte STRICTE du modèle :
    - le patient doit avoir consulté
    - une décision médicale est supposée prise
    """
    return patient.a_consulte()


def peut_etre_transfere_en_unite(
    patient: Patient,
    ressources: RessourcesService,
) -> bool:
    """
    Conditions nécessaires pour un transfert effectif :
    - patient éligible au transfert (consultation préalable)
    - unité correspondant à la spécialité existante
    - unité non saturée
    """
    if not patient.est_eligible_transfert_unite():
        return False

    unite = ressources.unites.get(patient.specialite_requise)
    if unite is None:
        return False

    return not unite.est_saturee


# ============================================================
# Contraintes ressources humaines (anticipation)
# ============================================================

def personnel_suffisant_pour_consultation(
    ressources: RessourcesService,
) -> bool:
    """
    Règle organisationnelle :
    - un médecin est obligatoire
    - un infirmier OU un aide-soignant peut assister
    """
    if not ressources.medecin_disponible:
        return False

    # Anticipation du modèle RH :
    # un aide-soignant peut remplacer un infirmier
    return ressources.infirmier_disponible or ressources.aide_soignant_disponible
