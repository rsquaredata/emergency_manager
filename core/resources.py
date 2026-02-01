from core.enums import Localisation, Specialite


# ============================================================
# Ressources humaines
# ============================================================

class RessourceHumaine:
    """
    Classe de base pour toute ressource humaine.
    Une ressource ne peut être affectée qu'à un seul poste à la fois.
    """

    def __init__(self, identifiant: str):
        self.id = identifiant
        self.affectation = None  # type: Localisation | None

    @property
    def est_disponible(self) -> bool:
        return self.affectation is None

    def affecter(self, localisation: Localisation):
        if not self.est_disponible:
            raise RuntimeError(
                f"Ressource {self.id} déjà affectée à {self.affectation}"
            )
        self.affectation = localisation

    def liberer(self):
        self.affectation = None


class Medecin(RessourceHumaine):
    pass


class Infirmier(RessourceHumaine):
    pass


class AideSoignant(RessourceHumaine):
    pass


# ============================================================
# Ressources physiques
# ============================================================

class SalleAttente:
    """
    Salle d'attente à capacité STRICTE.
    """

    def __init__(self, localisation: Localisation, capacite_max: int):
        self.localisation = localisation
        self.capacite_max = capacite_max
        self.occupation = 0

    @property
    def est_saturee(self) -> bool:
        return self.occupation >= self.capacite_max

    def entrer(self):
        if self.est_saturee:
            raise RuntimeError(f"{self.localisation.value} saturée")
        self.occupation += 1

    def sortir(self):
        self.occupation = max(0, self.occupation - 1)


class UniteHospitaliere:
    """
    Unité aval avec capacité maximale de lits.
    """

    def __init__(self, specialite: Specialite, capacite_max: int):
        self.specialite = specialite
        self.capacite_max = capacite_max
        self.patients_presents = 0

    @property
    def est_saturee(self) -> bool:
        return self.patients_presents >= self.capacite_max

    def admettre_patient(self):
        if self.est_saturee:
            raise RuntimeError(f"Unité {self.specialite.value} saturée")
        self.patients_presents += 1

    def liberer_lit(self):
        self.patients_presents = max(0, self.patients_presents - 1)


# ============================================================
# Conteneur global des ressources
# ============================================================

class RessourcesService:
    """
    Conteneur de TOUTES les ressources du service d'urgences.
    Source unique de vérité pour la disponibilité.
    """

    def __init__(self, capacite_unite: int = 5):
        # -------------------------
        # Ressources humaines
        # -------------------------
        self.medecin = Medecin("medecin_1")
        self.infirmiers = [
            Infirmier("inf_1"),
            Infirmier("inf_2"),
        ]
        self.aides_soignants = [
            AideSoignant("as_1"),
            AideSoignant("as_2"),
        ]

        # -------------------------
        # Salles d'attente
        # -------------------------
        self.salles_attente = {
            Localisation.SA1: SalleAttente(Localisation.SA1, capacite_max=5),
            Localisation.SA2: SalleAttente(Localisation.SA2, capacite_max=10),
            Localisation.SA3: SalleAttente(Localisation.SA3, capacite_max=5),
        }

        # -------------------------
        # Unités hospitalières
        # -------------------------
        self.unites = {
            spec: UniteHospitaliere(spec, capacite_max=capacite_unite)
            for spec in Specialite
            if spec != Specialite.AUCUNE
        }

    # ========================================================
    # Helpers ressources humaines
    # ========================================================

    @property
    def medecin_disponible(self) -> bool:
        return self.medecin.est_disponible

    @property
    def infirmier_disponible(self) -> bool:
        return any(inf.est_disponible for inf in self.infirmiers)

    @property
    def aide_soignant_disponible(self) -> bool:
        return any(asg.est_disponible for asg in self.aides_soignants)

    def affecter_medecin_consultation(self):
        self.medecin.affecter(Localisation.CONSULTATION)

    def liberer_medecin(self):
        self.medecin.liberer()

    def affecter_personnel_salle(self, localisation: Localisation):
        """
        Affecte en priorité un infirmier, sinon un aide-soignant.
        """
        for inf in self.infirmiers:
            if inf.est_disponible:
                inf.affecter(localisation)
                return

        for asg in self.aides_soignants:
            if asg.est_disponible:
                asg.affecter(localisation)
                return

        raise RuntimeError("Aucun personnel disponible pour la salle")

    # ========================================================
    # Helpers salles d'attente
    # ========================================================

    def salle_disponible(self, localisation: Localisation) -> bool:
        return not self.salles_attente[localisation].est_saturee

    def entrer_en_salle_attente(self, localisation: Localisation):
        self.salles_attente[localisation].entrer()

    def sortir_de_salle_attente(self, localisation: Localisation):
        self.salles_attente[localisation].sortir()

    def occupation_sa(self) -> dict:
        """
        Retourne l'occupation actuelle des SA (utile pour métriques).
        """
        return {
            loc: salle.occupation
            for loc, salle in self.salles_attente.items()
        }
