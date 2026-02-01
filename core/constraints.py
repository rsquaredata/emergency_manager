from core.enums import EtatPatient, Specialite
from core.patient import Patient
from core.resources import RessourcesService

def peut_consulter(patient: Patient, ressources: RessourcesService) -> bool:
    """Vérifie si un patient peut entrer en consultation."""
    return (
        patient.etat_courant == EtatPatient.EN_ATTENTE and
        ressources.boxes_disponibles > 0 and
        ressources.medecin_disponible
    )

def peut_etre_hospitalise(patient: Patient, ressources: RessourcesService) -> bool:
    """Vérifie les contraintes de transfert vers une unité."""
    # Règle stricte : passage obligatoire par la consultation
    a_vu_medecin = any(h["etat"] == EtatPatient.EN_CONSULTATION.value for h in patient.historique)
    
    if not a_vu_medecin:
        return False
        
    # Vérification de la capacité de l'unité spécifique
    unite = ressources.unites.get(patient.specialite_requise)
    if unite and not unite.est_saturee:
        return True
        
    return False
