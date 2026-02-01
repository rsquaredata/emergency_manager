from core.enums import (
    EtatPatient,
    Localisation,
    Gravite,
)
from core.constraints import (
    doit_etre_oriente_exterieur,
    peut_entrer_en_soins_critiques,
    peut_entrer_en_consultation,
    peut_entrer_en_salle_attente,
    peut_aller_en_attente_transfert,
    peut_etre_transfere_en_unite,
)
from core.patient import Patient
from core.hospital import HospitalSystem


class Scheduler:
    """
    Ordonnanceur déterministe de référence.
    Applique exclusivement les règles définies dans constraints.py
    """

    def __init__(self, hospital: HospitalSystem):
        self.hospital = hospital

    # ========================================================
    # Ordonnancement principal (1 tick de simulation)
    # ========================================================

    def executer_cycle(self):
        """
        Exécute un cycle complet de décisions :
        1. Orientation initiale (IOA)
        2. Accès consultation ou SA
        3. Transferts vers unités si possible
        """

        self._traiter_arrivees()
        self._traiter_transferts_unites()

    # ========================================================
    # Étape 1 — Arrivées et triage IOA
    # ========================================================

    def _traiter_arrivees(self):
        for patient in self._patients_par_etat(EtatPatient.ARRIVE):

            # Cas GRIS : sortie immédiate
            if doit_etre_oriente_exterieur(patient):
                patient.transition_to(
                    EtatPatient.ORIENTE_EXTERIEUR,
                    Localisation.EXTERIEUR,
                    "Patient GRIS orienté hors système",
                )
                continue

            # Cas ROUGE : soins critiques directs
            if peut_entrer_en_soins_critiques(patient):
                patient.transition_to(
                    EtatPatient.SOINS_CRITIQUES,
                    Localisation.SOINS_CRITIQUES,
                    "Urgence vitale détectée (ROUGE)",
                )
                continue

            # Cas VERT / JAUNE : consultation prioritaire
            if peut_entrer_en_consultation(self.hospital.ressources):
                # Affectation médecin + personnel
                self.hospital.ressources.affecter_medecin_consultation()
                self.hospital.ressources.affecter_personnel_salle(
                    Localisation.CONSULTATION
                )

                patient.transition_to(
                    EtatPatient.EN_CONSULTATION,
                    Localisation.CONSULTATION,
                    "Accès direct à la consultation",
                )
                continue

            # Sinon : passage en salle d'attente (ordre SA3 -> SA2 -> SA1)
            self._placer_en_salle_attente(patient)

    # ========================================================
    # Étape 2 — Transferts vers unités hospitalières
    # ========================================================

    def _traiter_transferts_unites(self):
        for patient in self._patients_par_etat(EtatPatient.ATTENTE_TRANSFERT):

            if peut_etre_transfere_en_unite(patient, self.hospital.ressources):
                # Libération SA
                if patient.est_en_salle_attente():
                    self.hospital.ressources.sortir_de_salle_attente(
                        patient.localisation_courante
                    )

                # Admission unité
                unite = self.hospital.ressources.unites[
                    patient.specialite_requise
                ]
                unite.admettre_patient()

                patient.transition_to(
                    EtatPatient.EN_UNITE,
                    Localisation.UNITE,
                    "Transfert effectif vers unité hospitalière",
                )

    # ========================================================
    # Helpers internes
    # ========================================================

    def _placer_en_salle_attente(self, patient: Patient):
        """
        Place un patient dans la première salle d'attente disponible.
        """
        for salle in [
            Localisation.SA3,
            Localisation.SA2,
            Localisation.SA1,
        ]:
            if peut_entrer_en_salle_attente(salle, self.hospital.ressources):
                self.hospital.ressources.entrer_en_salle_attente(salle)
                self.hospital.ressources.affecter_personnel_salle(salle)

                patient.transition_to(
                    EtatPatient.EN_ATTENTE,
                    salle,
                    f"Placement en {salle.value}",
                )
                return

        # Cas extrême : aucune SA disponible
        patient.transition_to(
            EtatPatient.EN_ATTENTE,
            Localisation.EXTERIEUR,
            "Aucune salle d'attente disponible (saturation totale)",
        )

    def _patients_par_etat(self, etat: EtatPatient):
        return [
            p for p in self.hospital.patients.values()
            if p.etat_courant == etat
        ]

    # ========================================================
    # Orientation post-consultation (appel explicite)
    # ========================================================

    def orienter_apres_consultation(
        self,
        patient_id: str,
        hospitalisation: bool,
    ):
        """
        Applique la décision médicale après consultation.
        """
        patient = self.hospital.patients[patient_id]

        # Libération ressources consultation
        if patient.localisation_courante == Localisation.CONSULTATION:
            self.hospital.ressources.liberer_medecin()
            # NOTE : libération personnel salle possible ici

        if hospitalisation:
            if not peut_aller_en_attente_transfert(patient):
                raise RuntimeError(
                    "Transfert interdit : consultation préalable absente"
                )

            self._placer_en_salle_attente(patient)
            patient.transition_to(
                EtatPatient.ATTENTE_TRANSFERT,
                patient.localisation_courante,
                "Décision hospitalisation prise",
            )
        else:
            patient.transition_to(
                EtatPatient.SORTI,
                Localisation.EXTERIEUR,
                "Consultation terminée – sortie",
            )
