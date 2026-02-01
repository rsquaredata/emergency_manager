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

        # Gestion RH (présence indicative)
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
    """
    Unité d'hospitalisation aval.
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
    Source unique de vérité pour les ressources du service.
    """

    def __init__(self, capacite_unite: int = 5):
        # -------------------------
        # Ressources humaines
        # -------------------------
        self.medecin = Medecin("medecin_1")
        self.infirmiers = [Infirmier("inf_1"), Infirmier("inf_2")]
        self.aides_soignants = [AideSoignant("as_1"), AideSoignant("as_2")]

        # -------------------------
        # Salles d'attente
        # -------------------------
        self.salles_attente = {
            Localisation.SA1: SalleAttente(Localisation.SA1, 5),
            Localisation.SA2: SalleAttente(Localisation.SA2, 10),
            Localisation.SA3: SalleAttente(Localisation.SA3, 5),
        }

        # -------------------------
        # Unités aval
        # -------------------------
        self.unites = {
            spec: UniteHospitaliere(spec, capacite_unite)
            for spec in Specialite
            if spec != Specialite.AUCUNE
        }

        # -------------------------
        # Soins critiques
        # -------------------------
        self.capacite_soins_critiques = 8
        self.occupation_soins_critiques = 0

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

    def affecter_medecin_consultation(self):
        self.medecin.affecter(Localisation.CONSULTATION)

    def liberer_medecin(self):
        self.medecin.liberer()

    def affecter_personnel_salle(self, localisation: Localisation):
        """
        Affecte un infirmier sinon un aide-soignant à une salle.
        """
        for inf in self.infirmiers:
            if inf.est_disponible:
                inf.affecter(localisation)
                self.salles_attente[localisation].enregistrer_presence_personnel()
                return

        for asg in self.aides_soignants:
            if asg.est_disponible:
                asg.affecter(localisation)
                self.salles_attente[localisation].enregistrer_presence_personnel()
                return

        # Pas bloquant pour le modèle (présence tolérée < 15 min)
        self.salles_attente[localisation].enregistrer_absence_personnel()

    # ========================================================
    # Helpers salles d'attente
    # ========================================================

    def entrer_en_salle_attente(self, localisation: Localisation):
        self.salles_attente[localisation].entrer()

    def sortir_de_salle_attente(self, localisation: Localisation):
        self.salles_attente[localisation].sortir()

    def occupation_sa(self) -> dict:
        return {
            loc: salle.occupation
            for loc, salle in self.salles_attente.items()
        }

    # ========================================================
    # Soins critiques
    # ========================================================

    def soins_critiques_disponibles(self) -> bool:
        return self.occupation_soins_critiques < self.capacite_soins_critiques

    def admettre_soins_critiques(self):
        if not self.soins_critiques_disponibles():
            raise RuntimeError("Soins critiques saturés")
        self.occupation_soins_critiques += 1

    def liberer_soins_critiques(self):
        self.occupation_soins_critiques = max(
            0,
            self.occupation_soins_critiques - 1
        )
