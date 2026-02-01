from typing import List
from core.hospital import HospitalSystem
from core.enums import EtatPatient, Gravite
from core.constraints import peut_consulter, peut_etre_hospitalise

class Scheduler:
    def __init__(self, system: HospitalSystem):
        self.system = system

    def _ordonnancer_attente(self) -> List[str]:
        """Trie les IDs des patients en attente par score de priorité."""
        patients_en_attente = [
            p for p in self.system.patients.values() 
            if p.etat_courant == EtatPatient.EN_ATTENTE
        ]
        # Tri par score (Gravité + Temps) descendant
        sorted_patients = sorted(
            patients_en_attente, 
            key=lambda p: p.get_score_priorite(), 
            reverse=True
        )
        return [p.id for p in sorted_patients]

    def executer_cycle(self):
        """Logique principale exécutée à chaque tick de la simulation."""
        
        # 1. Gérer les sorties des unités (Simulation simplifiée)
        # Dans un vrai système, cela dépendrait d'un événement externe
        
        # 2. Tenter d'hospitaliser ceux qui attendent un transfert
        en_attente_transfert = [
            p for p in self.system.patients.values() 
            if p.etat_courant == EtatPatient.EN_ATTENTE_TRANSFERT
        ]
        for patient in en_attente_transfert:
            if peut_etre_hospitalise(patient, self.system.ressources):
                unite = self.system.ressources.unites[patient.specialite_requise]
                unite.patients_presents += 1
                patient.transition_to(
                    EtatPatient.EN_UNITE, 
                    f"Transfert vers l'unité de {patient.specialite_requise.value}"
                )
                self.system.ressources.liberer_box()

        # 3. Affecter les boxes aux patients les plus prioritaires
        ids_prioritaires = self._ordonnancer_attente()
        for p_id in ids_prioritaires:
            patient = self.system.patients[p_id]
            
            if peut_consulter(patient, self.system.ressources):
                self.system.ressources.occuper_box()
                patient.transition_to(
                    EtatPatient.EN_CONSULTATION, 
                    "Admission en box pour examen médical"
                )

    def simuler_decision_medicale(self, patient_id: str, hospitalisation_requise: bool):
        """Simule l'issue d'une consultation (IA ou Manuel)."""
        patient = self.system.patients.get(patient_id)
        if not patient or patient.etat_courant != EtatPatient.EN_CONSULTATION:
            return

        if hospitalisation_requise:
            patient.transition_to(
                EtatPatient.EN_ATTENTE_TRANSFERT, 
                "Hospitalisation décidée, en attente de lit"
            )
        else:
            self.system.ressources.liberer_box()
            patient.transition_to(EtatPatient.SORTI, "Fin de prise en charge, retour domicile")
