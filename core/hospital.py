from typing import List, Dict
from core.patient import Patient
from core.resources import RessourcesService
from core.enums import EtatPatient

class HospitalSystem:
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.ressources = RessourcesService()
        self.horloge_interne = 0  # En minutes depuis le lancement

    def ajouter_patient(self, patient: Patient):
        self.patients[patient.id] = patient
        patient.transition_to(EtatPatient.EN_ATTENTE, "Admis au service des urgences")

    def calculer_indice_saturation(self) -> float:
        """Calcule l'IS défini dans system_model.md."""
        p_actifs = [p for p in self.patients.values() if p.etat_courant != EtatPatient.SORTI]
        if not p_actifs:
            return 0.0
        # IS = (Patients en attente + Patients en Box) / Nombre de Box
        en_attente = len([p for p in p_actifs if p.etat_courant == EtatPatient.EN_ATTENTE])
        en_box = 3 - self.ressources.boxes_disponibles
        return round((en_attente + en_box) / 3, 2)

    def tick(self):
        """Fait avancer la simulation d'une minute."""
        self.horloge_interne += 1
        # Cette méthode sera appelée par la boucle principale
        # et déclenchera le scheduler
