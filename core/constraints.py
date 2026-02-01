from core.enums import Localisation, EtatPatient
from core.patient import Patient
from core.resources import RessourcesService

def peut_entrer_en_sa(salle: Localisation, ressources: RessourcesService) -> bool:
    return ressources.occupation_sa[salle] < ressources.capacites_sa[salle]

def peut_aller_en_unite(patient: Patient, ressources: RessourcesService) -> bool:
    unite = ressources.unites.get(patient.specialite_requise)
    return unite is not None and not unite.est_saturee
