from datetime import datetime
from typing import List, Dict
from core.enums import Gravite, EtatPatient, Specialite, Localisation

class Patient:
    def __init__(self, patient_id: str, gravite: Gravite, specialite: Specialite = Specialite.AUCUNE):
        self.id = patient_id
        self.gravite = gravite
        self.specialite_requise = specialite
        self.heure_arrivee = datetime.now()
        self.etat_courant = EtatPatient.ARRIVE
        self.localisation_courante = Localisation.EXTERIEUR
        self.historique: List[Dict] = []
        
        self._log_transition(EtatPatient.ARRIVE, Localisation.EXTERIEUR, "Initialisation")

    def _log_transition(self, etat: EtatPatient, loc: Localisation, raison: str):
        self.historique.append({
            "timestamp": datetime.now().isoformat(),
            "etat": etat.value,
            "localisation": loc.value,
            "raison": raison
        })

    def transition_to(self, nouvel_etat: EtatPatient, nouvelle_loc: Localisation, raison: str):
        self.etat_courant = nouvel_etat
        self.localisation_courante = nouvelle_loc
        self._log_transition(nouvel_etat, nouvelle_loc, raison)

    def get_score_priorite(self) -> float:
        delta = (datetime.now() - self.heure_arrivee).total_seconds() / 60
        return (self.gravite.value * 100) + delta
