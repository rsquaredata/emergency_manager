from datetime import datetime
from typing import List, Optional, Dict
from core.enums import Gravite, EtatPatient, Specialite

class Patient:
    def __init__(
        self, 
        patient_id: str, 
        gravite: Gravite, 
        specialite: Specialite = Specialite.AUCUNE
    ):
        self.id = patient_id
        self.gravite = gravite
        self.specialite_requise = specialite
        self.heure_arrivee = datetime.now()
        self.etat_courant = EtatPatient.ARRIVE
        self.historique: List[Dict] = []
        
        # Initialisation de l'historique
        self._enregistrer_transition(EtatPatient.ARRIVE, "Arrivée initiale")

    def _enregistrer_transition(self, nouvel_etat: EtatPatient, raison: str):
        timestamp = datetime.now().isoformat()
        self.historique.append({
            "timestamp": timestamp,
            "etat": nouvel_etat.value,
            "raison": raison
        })
        # Format de log pour le fichier decisions.log
        print(f"[{timestamp}] [TRANSITION] {self.id} -> {nouvel_etat.value}. Raison: {raison}")

    def transition_to(self, nouvel_etat: EtatPatient, raison: str):
        """Change l'état du patient et archive le mouvement."""
        self.etat_courant = nouvel_etat
        self._enregistrer_transition(nouvel_etat, raison)

    @property
    def temps_attente_minutes(self) -> float:
        delta = datetime.now() - self.heure_arrivee
        return round(delta.total_seconds() / 60, 2)

    def get_score_priorite(self) -> float:
        """Calcul déterministe de la priorité."""
        return (self.gravite.value * 100) + self.temps_attente_minutes
