from datetime import datetime
from core.enums import EtatPatient, Localisation
from core.resources import RessourcesService


class HospitalSystem:
    """
    Représente l'état global du service d'urgences.
    Source unique de vérité pour :
    - les patients
    - les ressources
    - les métriques
    """

    def __init__(self, capacite_unite: int = 5):
        # -------------------------
        # Temps de simulation
        # -------------------------
        self.tick = 0
        self.now = datetime.now()

        # -------------------------
        # État système
        # -------------------------
        self.patients = {}
        self.ressources = RessourcesService(capacite_unite=capacite_unite)

    # ========================================================
    # Gestion du temps (simulation)
    # ========================================================

    def avancer_temps(self, tick: int):
        """
        Synchronise le temps logique de la simulation.
        """
        self.tick = tick
        self.now = datetime.now()

    # ========================================================
    # Gestion des patients
    # ========================================================

    def ajouter_patient(self, patient):
        self.patients[patient.id] = patient

    # ========================================================
    # MÉTRIQUES — INDICES DE SATURATION
    # ========================================================

    def calculer_is_sa(self) -> float:
        """
        IS_SA = occupation totale des salles d'attente
                / capacité totale des salles d'attente
        Indicateur local, borné.
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

    def calculer_is_global(self) -> float:
        """
        IS_GLOBAL = backlog / capacité d'absorption totale
        Indicateur débordant.
        """
        backlog = sum(
            1 for p in self.patients.values()
            if p.etat_courant in [
                EtatPatient.EN_ATTENTE,
                EtatPatient.ATTENTE_TRANSFERT,
            ]
        )

        cap_sa = sum(
            salle.capacite_max
            for salle in self.ressources.salles_attente.values()
        )

        cap_aval = sum(
            unite.capacite_max
            for unite in self.ressources.unites.values()
        )

        denom = cap_sa + cap_aval
        return round(backlog / denom, 2) if denom > 0 else 0.0

    def calculer_overflow_aval(self) -> float:
        """
        Overflow aval = patients en attente de transfert
                        / capacité totale des unités aval
        """
        attente_transfert = sum(
            1 for p in self.patients.values()
            if p.etat_courant == EtatPatient.ATTENTE_TRANSFERT
        )

        cap_aval = sum(
            unite.capacite_max
            for unite in self.ressources.unites.values()
        )

        return round(attente_transfert / cap_aval, 2) if cap_aval > 0 else 0.0

    # ========================================================
    # COMPTEURS PATIENTS (features ML)
    # ========================================================

    def _compter_patients_par_etat(self) -> dict:
        compteurs = {
            EtatPatient.ARRIVE: 0,
            EtatPatient.EN_ATTENTE: 0,
            EtatPatient.EN_CONSULTATION: 0,
            EtatPatient.ATTENTE_TRANSFERT: 0,
            EtatPatient.EN_UNITE: 0,
            EtatPatient.SORTI: 0,
            EtatPatient.ORIENTE_EXTERIEUR: 0,
        }

        for p in self.patients.values():
            if p.etat_courant in compteurs:
                compteurs[p.etat_courant] += 1

        return compteurs

    def _compteurs_derives(self) -> dict:
        c = self._compter_patients_par_etat()

        return {
            "nb_patients_total": len(self.patients),
            "nb_en_attente": c[EtatPatient.EN_ATTENTE],
            "nb_en_consultation": c[EtatPatient.EN_CONSULTATION],
            "nb_attente_transfert": c[EtatPatient.ATTENTE_TRANSFERT],
            "nb_en_unite": c[EtatPatient.EN_UNITE],
            "nb_sortis": c[EtatPatient.SORTI],
        }

    # ========================================================
    # OCCUPATION DES RESSOURCES
    # ========================================================

    def _occupation_ressources(self) -> dict:
        occupation_sa = self.ressources.occupation_sa()

        occupation_unites = {
            spec.value: unite.patients_presents
            for spec, unite in self.ressources.unites.items()
        }

        return {
            "occupation_sa_total": sum(occupation_sa.values()),
            "occupation_sa1": occupation_sa.get(Localisation.SA1, 0),
            "occupation_sa2": occupation_sa.get(Localisation.SA2, 0),
            "occupation_sa3": occupation_sa.get(Localisation.SA3, 0),
            "occupation_unites_total": sum(occupation_unites.values()),
            **occupation_unites,
        }

    # ========================================================
    # SNAPSHOT GLOBAL (BASE ML)
    # ========================================================

    def snapshot_etat(self) -> dict:
        """
        État global du système à un instant t.
        Chaque snapshot = 1 ligne de dataset ML.
        """
        snapshot = {
            "tick": self.tick,
            "time": self.now.isoformat(),

            # Indicateurs globaux
            "is_sa": self.calculer_is_sa(),
            "is_global": self.calculer_is_global(),
            "overflow_aval": self.calculer_overflow_aval(),

            # Ressources humaines (binaire, ML-friendly)
            "medecin_disponible": int(self.ressources.medecin_disponible),
            "infirmier_disponible": int(self.ressources.infirmier_disponible),
            "aide_soignant_disponible": int(self.ressources.aide_soignant_disponible),
        }

        snapshot.update(self._compteurs_derives())
        snapshot.update(self._occupation_ressources())

        return snapshot
