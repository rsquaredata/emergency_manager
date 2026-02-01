from datetime import datetime, timedelta

from core.enums import (
    Localisation,
    Gravite,
)
from core.patient import Patient
from core.resources import RessourcesService


# ============================================================
# Contraintes salles d'attente (capacités physiques)
# ============================================================

def peut_entrer_en_salle_attente(
    salle: Localisation,
    ressources: RessourcesService,
) -> bool:
    """
    Contrainte stricte :
    - la salle ne doit pas être saturée physiquement.
    Les ressources humaines ne bloquent PAS l'entrée.
    """
    return ressources.salle_disponible(salle)


# ============================================================
# Contraintes consultation
# ============================================================

def peut_entrer_en_consultation(
    ressources: RessourcesService,
) -> bool:
    """
    Une consultation nécessite un médecin disponible.
    """
    return ressources.medecin_disponible


# ============================================================
# Contraintes soins critiques
# ============================================================

def peut_entrer_en_soins_critiques(patient: Patient) -> bool:
    """
    Seuls les patients ROUGE peuvent entrer directement
    en soins critiques.
    """
    return patient.gravite == Gravite.ROUGE


# ============================================================
# Contraintes orientation externe
# ============================================================

def doit_etre_oriente_exterieur(patient: Patient) -> bool:
    """
    Les patients GRIS sont orientés hors du système.
    """
    return patient.gravite == Gravite.GRIS


# ============================================================
# Contraintes hospitalisation / unités aval
# ============================================================

def peut_aller_en_attente_transfert(patient: Patient) -> bool:
    """
    Contrainte stricte :
    - le patient doit avoir consulté.
    """
    return patient.a_consulte()


def peut_etre_transfere_en_unite(
    patient: Patient,
    ressources: RessourcesService,
) -> bool:
    """
    Conditions de transfert effectif :
    - consultation préalable
    - unité existante
    - unité non saturée
    """
    if not patient.est_eligible_transfert_unite():
        return False

    unite = ressources.unites.get(patient.specialite_requise)
    if unite is None:
        return False

    return not unite.est_saturee


# ============================================================
# Contraintes de conformité RH salles d'attente
# ============================================================

def salle_attente_conforme(
    salle: Localisation,
    ressources: RessourcesService,
    maintenant: datetime,
) -> bool:
    """
    Une salle d'attente est conforme si :
    - elle est vide
    - OU personnel présent
    - OU absence de personnel < 15 minutes
    """
    sa = ressources.salles_attente[salle]

    if sa.occupation == 0:
        return True

    if sa.personnel_present:
        return True

    if sa.derniere_presence_personnel is None:
        return False

    return (maintenant - sa.derniere_presence_personnel) <= timedelta(minutes=15)
