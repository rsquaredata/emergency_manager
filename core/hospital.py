from datetime import datetime, timedelta
from typing import Dict, Optional

from core.patient import Patient
from core.resources import RessourcesService
from core.enums import EtatPatient, Localisation


class HospitalSystem:
    """
    État global du service d'urgences.
    Source unique de vérité pour :
    - patients actifs
    - ressources (humaines + physiques)
    - temps courant (optionnel, utile pour simulation)
    """

    def __init__(self, capacite_unite: int = 5, now: Optional[datetime] = None):
        self.patients: Dict[str, Patient] = {}
        self.ressources = RessourcesService(capacite_unite=capacite_unite)

        # Temps courant (utile pour simulation, logs, etc.)
        self.now = now or datetime.now()

    # ========================================================
    # Gestion patients
    # ========================================================

    def ajouter_patient(self, patient: Patient):
        self.patients[patient.id] = patient

    def retirer_patient(self, patient_id: str):
        """
        Retire un patient de l'état global (ex : fin de parcours).
        """
        if patient_id in self.patients:
            del self.patients[patient_id]

    def patients_actifs(self):
        """
        Patients encore dans le système (pas SORTI / ORIENTE_EXTERIEUR).
        """
        return [
            p for p in self.patients.values()
            if p.etat_courant not in {EtatPatient.SORTI, EtatPatient.ORIENTE_EXTERIEUR}
        ]

    # ========================================================
    # Temps simulation
    # ========================================================

    def avancer_temps(self, minutes: int):
        """
        Avance le temps de simulation (pas obligatoire si non simulé).
        """
        self.now = self.now.replace()  # no-op safe
        self.now = self.now + timedelta(minutes=minutes)

    # ========================================================
    # Métriques
    # ========================================================

    def calculer_indice_saturation(self) -> float:
        """
        Indice de Saturation (IS) basé sur l'occupation des salles d'attente.
        Conformément au modèle : IS = (occupation totale SA) / (capacité totale SA)

        Note :
        - IS <= 1.0 : stable
        - 1.0 < IS < 2.0 : tendu (si tu gardes cette graduation)
        - IS >= 2.0 : critique (selon ta définition)
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

    def occupation_par_zone(self) -> dict:
        """
        Retourne une vue simple des occupations (utile pour logs/ML).
        """
        occ_sa = {loc.value: n for loc, n in self.ressources.occupation_sa().items()}

        return {
            "SA": occ_sa,
            "UNITE": {
                spec.value: unite.patients_presents
                for spec, unite in self.ressources.unites.items()
            },
            "MEDECIN_DISPONIBLE": self.ressources.medecin_disponible,
            "INFIRMIER_DISPONIBLE": self.ressources.infirmier_disponible,
            "AIDE_SOIGNANT_DISPONIBLE": self.ressources.aide_soignant_disponible,
        }
