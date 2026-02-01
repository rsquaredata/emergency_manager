from datetime import datetime
from core.enums import Localisation, Specialite


# ============================================================
# Ressources humaines
# ============================================================

class RessourceHumaine:
    def __init__(self, identifiant: str):
        self.id = identifiant
        self.affectation = None

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
    Salle d'attente à capacité stricte.
    Le personnel est affecté à la salle, pas aux patients.
    """

    def __init__(self, localisation: Localisation, capacite_max: int):
        self.localisation = localisation
        self.capacite_max = capacite_max
        self.occupation = 0

        # Gestion RH
        self.personnel_present = False
        self.derniere_presence_personnel = None

    @property
    def est_saturee(self) -> bool:
        return self.occupation >= self.capacite_max

    def entrer(self):
        if self.est_saturee:
            raise RuntimeError(f"{self.localisation.value} saturée")
        self.occupation += 1

    def sortir(self):
        self.occupation = max(0, self.occupation - 1)

    def enregistrer_presence_personnel(self):
        self.personnel_present = True
        self.derniere_presence_personnel = datetime.now()

    def enregistrer_absence_personnel(self):
        self.personnel_present = False
        self.derniere_presence_personnel = datetime.now()


class UniteHospitaliere:
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
    Source unique de vérité pour les ressources.
    """

    def __init__(self, capacite_unite: int = 5):
        # RH
        self.medecin = Medecin("medecin_1")
        self.infirmiers = [Infirmier("inf_1"), Infirmier("inf_2")]
        self.aides_soignants = [AideSoignant("as_1"), AideSoignant("as_2")]

        # Salles d'attente
        self.salles_attente = {
            Localisation.SA1: SalleAttente(Localisation.SA1, 5),
            Localisation.SA2: SalleAttente(Localisation.SA2, 10),
            Localisation.SA3: SalleAttente(Localisation.SA3, 5),
        }

        # Unités
        self.unites = {
            spec: UniteHospitaliere(spec, capacite_unite)
            for spec in Specialite
            if spec != Specialite.AUCUNE
        }
    
    def affecter_medecin_consultation(self):
        """
        Affecte le médecin à la consultation.
        """
        self.medecin.affecter(Localisation.CONSULTATION)
    
    def liberer_medecin(self):
        self.medecin.liberer()

    # ========================================================
    # Helpers RH
    # ========================================================

    @property
    def medecin_disponible(self) -> bool:
        return self.medecin.est_disponible

    @property
    def infirmier_disponible(self) -> bool:
        return any(i.est_disponible for i in self.infirmiers)

    @property
    def aide_soignant_disponible(self) -> bool:
        return any(a.est_disponible for a in self.aides_soignants)

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
        return {
            loc: salle.occupation
            for loc, salle in self.salles_attente.items()
        }
