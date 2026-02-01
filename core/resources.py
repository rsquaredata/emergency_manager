from core.enums import Specialite, Localisation

class UniteHospitaliere:
    def __init__(self, nom: Specialite, capacite_max: int):
        self.nom = nom
        self.capacite_max = capacite_max
        self.patients_presents = 0

    @property
    def est_saturee(self) -> bool:
        return self.patients_presents >= self.capacite_max

class RessourcesService:
    def __init__(self, n_hospital_capacity: int = 10):
        # Salles d'Attente (Capacités strictes Sujet 3)
        self.capacites_sa = {Localisation.SA1: 5, Localisation.SA2: 10, Localisation.SA3: 5}
        self.occupation_sa = {Localisation.SA1: 0, Localisation.SA2: 0, Localisation.SA3: 0}
        
        self.medecin_disponible = True
        self.soins_critiques_occupes = 0 # Capacité souple
        
        self.unites = {spec: UniteHospitaliere(spec, n_hospital_capacity) for spec in Specialite if spec != Specialite.AUCUNE}

    def modifier_occupation_sa(self, salle: Localisation, delta: int):
        if salle in self.occupation_sa:
            self.occupation_sa[salle] = max(0, self.occupation_sa[salle] + delta)
