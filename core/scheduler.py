from core.enums import (
    EtatPatient,
    Localisation,
    Gravite,
)
from core.constraints import (
    peut_entrer_en_salle_attente,
    peut_entrer_en_consultation,
    peut_entrer_en_soins_critiques,
    doit_etre_oriente_exterieur,
    peut_aller_en_attente_transfert,
    peut_etre_transfere_en_unite,
)
from core.patient import Patient


class Scheduler:
    """
    Ordonnanceur déterministe de référence.
    Applique strictement les règles du system_model.
    """

    def __init__(self, hospital):
        self.hospital = hospital

    # ============================================================
    # Cycle principal
    # ============================================================

    def executer_cycle(self):
        """
        Exécute un cycle complet de décisions :
        1. Traitement des arrivées (IOA)
        2. Orientation consultation ou salles d'attente
        3. Transferts vers unités aval si possible
        """
        self._traiter_arrivees()
        self._traiter_transferts_unites()

    # ============================================================
    # Étape 1 — Arrivées et triage IOA
    # ============================================================

    def _traiter_arrivees(self):
        """
        Applique les règles de triage aux patients ARRIVE.
        """
        for patient in self.hospital.patients.values():
            if patient.etat_courant != EtatPatient.ARRIVE:
                continue

            # ----------------------------
            # Cas GRIS : sortie immédiate
            # ----------------------------
            if doit_etre_oriente_exterieur(patient):
                patient.transition_to(
                    EtatPatient.ORIENTE_EXTERIEUR,
                    Localisation.EXTERIEUR,
                    "Patient GRIS orienté hors système",
                )
                continue

            # ----------------------------
            # Cas ROUGE : soins critiques
            # ----------------------------
            if peut_entrer_en_soins_critiques(patient):
                patient.transition_to(
                    EtatPatient.SOINS_CRITIQUES,
                    Localisation.SOINS_CRITIQUES,
                    "Urgence vitale détectée (ROUGE)",
                )
                continue

            # ----------------------------
            # Cas VERT / JAUNE : consultation prioritaire
            # ----------------------------
            if peut_entrer_en_consultation(self.hospital.ressources):
                # Affectation explicite du médecin
                self.hospital.ressources.affecter_medecin_consultation()

                patient.transition_to(
                    EtatPatient.EN_CONSULTATION,
                    Localisation.CONSULTATION,
                    "Accès direct à la consultation",
                )
                continue

            # ----------------------------
            # Sinon : salle d'attente
            # ----------------------------
            self._placer_en_salle_attente(patient)

    # ============================================================
    # Placement en salle d'attente
    # ============================================================

    def _placer_en_salle_attente(self, patient: Patient):
        """
        Place un patient dans la première salle d'attente disponible.
        Ordre volontaire : SA3 → SA2 → SA1 (logique de délestage).
        """
        for salle in (
            Localisation.SA3,
            Localisation.SA2,
            Localisation.SA1,
        ):
            if peut_entrer_en_salle_attente(
                salle, self.hospital.ressources
            ):
                self.hospital.ressources.entrer_en_salle_attente(salle)

                patient.transition_to(
                    EtatPatient.EN_ATTENTE,
                    salle,
                    f"Placement en {salle.value}",
                )
                return

        # Si aucune salle n'est disponible → stagnation externe
        patient.transition_to(
            EtatPatient.ATTENTE_TRANSFERT,
            Localisation.EXTERIEUR,
            "Aucune salle d'attente disponible",
        )

    # ============================================================
    # Étape 2 — Transferts vers unités aval
    # ============================================================

    def _traiter_transferts_unites(self):
        """
        Tente de transférer les patients en attente de transfert
        vers les unités hospitalières si possible.
        """
        for patient in self.hospital.patients.values():
            if patient.etat_courant != EtatPatient.ATTENTE_TRANSFERT:
                continue

            if peut_etre_transfere_en_unite(
                patient, self.hospital.ressources
            ):
                unite = self.hospital.ressources.unites[
                    patient.specialite_requise
                ]
                unite.admettre_patient()

                patient.transition_to(
                    EtatPatient.EN_UNITE,
                    Localisation.UNITE,
                    "Transfert vers unité hospitalière",
                )
