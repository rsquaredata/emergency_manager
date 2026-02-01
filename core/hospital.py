from datetime import datetime, timedelta
from typing import Dict, Optional

from core.patient import Patient
from core.resources import RessourcesService
from core.enums import EtatPatient


class HospitalSystem:
    """
    État global du service d'urgences.

    Responsabilités :
    - stocker les patients
    - stocker les ressources
    - gérer le temps simulé
    - calculer les métriques (IS)
    """

    def __init__(
        self,
        capacite_unite: int = 5,
        minutes_par_tick: int = 5,
        start_time: Optional[datetime] = None,
    ):
        # -------------------------
        # État global
        # -------------------------
        self.patients: Dict[str, Patient] = {}
        self.ressources = RessourcesService(capacite_unite=capacite_unite)

        # -------------------------
        # Temps simulé
        # -------------------------
        self.minutes_par_tick = minutes_par_tick
        self.tick = 0

        self.start_time = start_time or datetime.now()
        self.now = self.start_time

    # ========================================================
    # Gestion du temps
    # ========================================================

    def avancer_d_un_tick(self):
        """
        Avance le temps simulé d'un tick.
        1 tick = minutes_par_tick minutes simulées.
        """
        self.tick += 1
        self.now = self.start_time + timedelta(
            minutes=self.tick * self.minutes_par_tick
        )

    # ========================================================
    # Gestion des patients
    # ========================================================

    def ajouter_patient(self, patient: Patient):
        self.patients[patient.id] = patient

    def retirer_patient(self, patient_id: str):
        if patient_id in self.patients:
            del self.patients[patient_id]

    def patients_actifs(self):
        """
        Patients encore dans le système.
        """
        return [
            p for p in self.patients.values()
            if p.etat_courant not in {
                EtatPatient.SORTI,
                EtatPatient.ORIENTE_EXTERIEUR,
            }
        ]

    # ========================================================
    # Métriques
    # ========================================================

    def calculer_indice_saturation(self) -> float:
        """
        IS = occupation totale SA / capacité totale SA
        """
        occupation = self.ressources.occupation_sa()
        total_occ = sum(occupation.values())

        total_cap = sum(
            salle.capacite_max
            for salle in self.ressources.salles_attente.values()
        )

        if total_cap == 0:
            return 0.0

        return round(total_occ / total_cap, 2)

    def snapshot_etat(self) -> dict:
        """
        État compact du système à un instant donné.
        Utile pour logs, ML, visualisation.
        """
        return {
            "tick": self.tick,
            "time": self.now.isoformat(),
            "indice_saturation": self.calculer_indice_saturation(),
            "occupation_sa": {
                loc.value: salle.occupation
                for loc, salle in self.ressources.salles_attente.items()
            },
            "unites": {
                spec.value: unite.patients_presents
                for spec, unite in self.ressources.unites.items()
            },
            "medecin_disponible": self.ressources.medecin_disponible,
            "infirmier_disponible": self.ressources.infirmier_disponible,
            "aide_soignant_disponible": self.ressources.aide_soignant_disponible,
        }
