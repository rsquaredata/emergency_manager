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
    peut_etre_transfere_en_unite,
)
from core.patient import Patient
from core.stay import tirer_duree_sejour, TypeSejour


class Scheduler:
    """
    Ordonnanceur déterministe de référence.
    Applique les règles du system_model.
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
        self._traiter_sorties()

    # ============================================================
    # Étape 1 — Arrivées et triage IOA
    # ============================================================

    def _traiter_arrivees(self):
        for patient in list(self.hospital.patients.values()):
            if patient.etat_courant != EtatPatient.ARRIVE:
                continue

            # GRIS -> orienté extérieur
            if doit_etre_oriente_exterieur(patient):
                patient.transition_to(
                    EtatPatient.ORIENTE_EXTERIEUR,
                    Localisation.EXTERIEUR,
                    "Patient GRIS orienté hors système",
                )
                continue

            # ROUGE -> soins critiques
            if peut_entrer_en_soins_critiques(patient):
                self.hospital.ressources.admettre_soins_critiques()

                patient.tick_entree = self.hospital.tick
                patient.duree_sejour = tirer_duree_sejour(
                    TypeSejour.SOINS_CRITIQUES
                )

                patient.transition_to(
                    EtatPatient.SOINS_CRITIQUES,
                    Localisation.SOINS_CRITIQUES,
                    "Urgence vitale détectée (ROUGE)",
                )
                continue


            # VERT/JAUNE -> consultation prioritaire si possible
            if peut_entrer_en_consultation(self.hospital.ressources):
                self.hospital.ressources.affecter_medecin_consultation()
                patient.transition_to(
                    EtatPatient.EN_CONSULTATION,
                    Localisation.CONSULTATION,
                    "Accès direct à la consultation",
                )
                continue

            # Sinon -> SA
            self._placer_en_salle_attente(patient)

    # ============================================================
    # Placement en salle d'attente
    # ============================================================

    def _placer_en_salle_attente(self, patient: Patient):
        for salle in (
            Localisation.SA3,
            Localisation.SA2,
            Localisation.SA1,
        ):
            if peut_entrer_en_salle_attente(salle, self.hospital.ressources):
                self.hospital.ressources.entrer_en_salle_attente(salle)
                patient.transition_to(
                    EtatPatient.EN_ATTENTE,
                    salle,
                    f"Placement en {salle.value}",
                )
                return

        # Situation dégradée : plus de place
        patient.transition_to(
            EtatPatient.ATTENTE_TRANSFERT,
            Localisation.EXTERIEUR,
            "Aucune salle d'attente disponible",
        )

    # ============================================================
    # Orientation après consultation (décision médicale)
    # ============================================================

    def orienter_apres_consultation(
        self,
        patient_id: str,
        hospitalisation: bool,
    ):
        """
        Applique la décision médicale après consultation.
        """
        patient = self.hospital.patients[patient_id]

        if patient.etat_courant != EtatPatient.EN_CONSULTATION:
            raise RuntimeError(
                f"Orientation impossible : patient {patient.id} "
                f"n'est pas en consultation (etat={patient.etat_courant})."
            )

        # La consultation se termine -> libération médecin
        self.hospital.ressources.liberer_medecin()

        if not hospitalisation:
            patient.transition_to(
                EtatPatient.SORTI,
                Localisation.EXTERIEUR,
                "Fin consultation -> sortie",
            )
            return

        # Hospitalisation -> attente transfert en SA
        for salle in (
            Localisation.SA2,
            Localisation.SA3,
            Localisation.SA1,
        ):
            if peut_entrer_en_salle_attente(salle, self.hospital.ressources):
                self.hospital.ressources.entrer_en_salle_attente(salle)
                patient.transition_to(
                    EtatPatient.ATTENTE_TRANSFERT,
                    salle,
                    "Décision hospitalisation -> attente transfert en SA",
                )
                return

        patient.transition_to(
            EtatPatient.ATTENTE_TRANSFERT,
            Localisation.EXTERIEUR,
            "Décision hospitalisation -> aucune SA disponible",
        )

    # ============================================================
    # Étape 2 — Transferts vers unités aval
    # ============================================================

    def _traiter_transferts_unites(self):
        for patient in list(self.hospital.patients.values()):
            if patient.etat_courant != EtatPatient.ATTENTE_TRANSFERT:
                continue

            if peut_etre_transfere_en_unite(patient, self.hospital.ressources):
                unite = self.hospital.ressources.unites[patient.specialite_requise]
                unite.admettre_patient()

                patient.tick_entree = self.hospital.tick
                patient.duree_sejour = tirer_duree_sejour(
                TypeSejour.UNITE
                )

                patient.transition_to(
                    EtatPatient.EN_UNITE,
                    Localisation.UNITE,
                    "Transfert vers unité hospitalière",
                )

    # ============================================================
    # Sorties d'hospitalisation
    # ============================================================

    def _traiter_sorties(self):
        """
        Gère les sorties des patients après durée de séjour (unités et soins critiques).
        """
        for patient in list(self.hospital.patients.values()):

            if patient.etat_courant not in (
                EtatPatient.EN_UNITE,
                EtatPatient.SOINS_CRITIQUES,
            ):
                continue

            if patient.tick_entree is None or patient.duree_sejour is None:
                continue

            if self.hospital.tick - patient.tick_entree >= patient.duree_sejour:

                # Libération ressources
                if patient.etat_courant == EtatPatient.EN_UNITE:
                    unite = self.hospital.ressources.unites[
                        patient.specialite_requise
                    ]
                    unite.liberer_lit()

                elif patient.etat_courant == EtatPatient.SOINS_CRITIQUES:
                    self.hospital.ressources.liberer_soins_critiques()

                patient.transition_to(
                    EtatPatient.SORTI,
                    Localisation.EXTERIEUR,
                    "Sortie après durée de séjour",
                )
