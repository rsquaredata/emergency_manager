from datetime import datetime
from typing import List, Dict

from core.enums import Gravite, EtatPatient, Specialite, Localisation


class Patient:
    def __init__(
        self,
        patient_id: str,
        gravite: Gravite,
        specialite: Specialite = Specialite.AUCUNE,
    ):
        self.id = patient_id
        self.gravite = gravite
        self.specialite_requise = specialite

        self.heure_arrivee = datetime.now()

        self.etat_courant = EtatPatient.ARRIVE
        self.localisation_courante = Localisation.EXTERIEUR

        self.historique: List[Dict] = []

        self._log_transition(
            etat=self.etat_courant,
            localisation=self.localisation_courante,
            raison="Initialisation du patient",
        )

    # ------------------------------------------------------------------
    # Journalisation / traçabilité
    # ------------------------------------------------------------------

    def _log_transition(
        self,
        etat: EtatPatient,
        localisation: Localisation,
        raison: str,
    ):
        self.historique.append(
            {
                "timestamp": datetime.now().isoformat(),
                "etat": etat.value,
                "localisation": localisation.value,
                "raison": raison,
            }
        )

    # ------------------------------------------------------------------
    # Transitions d'état
    # ------------------------------------------------------------------

    def transition_to(
        self,
        nouvel_etat: EtatPatient,
        nouvelle_localisation: Localisation,
        raison: str,
    ):
        """
        Effectue une transition d'état.
        Toute validation métier lourde doit être faite en amont
        (scheduler + constraints).
        """
        self.etat_courant = nouvel_etat
        self.localisation_courante = nouvelle_localisation
        self._log_transition(nouvel_etat, nouvelle_localisation, raison)

    # ------------------------------------------------------------------
    # Règles métier locales (source de vérité patient)
    # ------------------------------------------------------------------

    def est_en_salle_attente(self) -> bool:
        return self.localisation_courante in {
            Localisation.SA1,
            Localisation.SA2,
            Localisation.SA3,
        }

    def a_consulte(self) -> bool:
        """
        Vérifie si le patient est déjà passé par la consultation.
        Condition STRICTE avant tout transfert vers une unité.
        """
        return any(
            entry["etat"] == EtatPatient.EN_CONSULTATION.value
            for entry in self.historique
        )

    def est_eligible_transfert_unite(self) -> bool:
        """
        Règle du modèle :
        - consultation obligatoire
        - spécialité requise connue
        """
        return self.a_consulte() and self.specialite_requise != Specialite.AUCUNE

    # ------------------------------------------------------------------
    # Priorisation
    # ------------------------------------------------------------------

    def temps_attente_minutes(self) -> float:
        return (datetime.now() - self.heure_arrivee).total_seconds() / 60.0

    def score_priorite(self) -> float:
        """
        Score utilisé par l'ordonnanceur :
        gravité (pondération forte) + temps d'attente.
        """
        return (self.gravite.value * 100.0) + self.temps_attente_minutes()
