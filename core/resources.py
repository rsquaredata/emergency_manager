from typing import Dict
from core.enums import Specialite

class UniteHospitaliere:
    def __init__(self, nom: Specialite, capacite_max: int):
        self.nom = nom
        self.capacite_max = capacite_max
        self.patients_presents: int = 0
        self.seuil_alerte = 0.9  # 90%

    @property
    def taux_occupation(self) -> float:
        return self.patients_presents / self.capacite_max

    @property
    def est_saturee(self) -> bool:
        return self.patients_presents >= self.capacite_max

    @property
    def alerte_seuil_atteint(self) -> bool:
        return self.taux_occupation >= self.seuil_alerte

class RessourcesService:
    def __init__(self):
        # Configuration conforme au system_model.md
        self.boxes_disponibles = 3
        self.medecin_disponible = True
        self.infirmiers_salle = 2
        
        # Unités de spécialité
        self.unites: Dict[Specialite, UniteHospitaliere] = {
            Specialite.CARDIOLOGIE: UniteHospitaliere(Specialite.CARDIOLOGIE, 5),
            Specialite.NEUROLOGIE: UniteHospitaliere(Specialite.NEUROLOGIE, 5),
            Specialite.PNEUMOLOGIE: UniteHospitaliere(Specialite.PNEUMOLOGIE, 5),
            Specialite.ORTHOPEDIE: UniteHospitaliere(Specialite.ORTHOPEDIE, 5),
        }

    def occuper_box(self):
        if self.boxes_disponibles > 0:
            self.boxes_disponibles -= 1
            
    def liberer_box(self):
        if self.boxes_disponibles < 3:
            self.boxes_disponibles += 1
