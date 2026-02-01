from core.resources import RessourcesService

class HospitalSystem:
    def __init__(self, capacite_n: int = 10):
        self.patients = {}
        self.ressources = RessourcesService(n_hospital_capacity=capacite_n)

    def ajouter_patient(self, patient):
        self.patients[patient.id] = patient

    def calculer_indice_saturation(self) -> float:
        total_sa = sum(self.ressources.occupation_sa.values())
        cap_sa = sum(self.ressources.capacites_sa.values()) # 20
        # IS basé sur l'occupation des 3 Salles d'Attente
        return round(total_sa / cap_sa, 2)
