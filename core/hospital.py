# core/hospital.py

class HospitalSystem:
    def __init__(self, capacite_n: int = 10):
        self.patients = {}
        # On passe N au service de ressources
        self.ressources = RessourcesService(capacite_unites=capacite_n)
        self.horloge_interne = 0

    def calculer_indice_saturation(self) -> float:
        """
        IS = (Patients en SA1+SA2+SA3 + Patients en Soins Critiques) / (Capacité totale SA)
        """
        en_attente = sum(self.ressources.occupation_salles.values())
        en_soins = self.ressources.patients_en_soins_critiques
        capacite_totale_sa = sum(self.ressources.capacites_salles.values()) # 30
        
        return round((en_attente + en_soins) / capacite_totale_sa, 2)
