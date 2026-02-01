from core.enums import EtatPatient, Localisation, Gravite
from core.constraints import peut_entrer_en_sa, peut_aller_en_unite

class Scheduler:
    def __init__(self, hospital):
        self.hospital = hospital

    def trier_priorites(self, salle_loc: Localisation):
        # Liste des patients dans une SA spécifique
        patients = [p for p in self.hospital.patients.values() if p.localisation_courante == salle_loc]
        return sorted(patients, key=lambda x: x.get_score_priorite(), reverse=True)

    def executer_cycle(self):
        # 1. Triage IOA vers flux directs ou SA
        for p in [p for p in self.hospital.patients.values() if p.etat_courant == EtatPatient.ARRIVE]:
            if p.gravite == Gravite.ROUGE:
                p.transition_to(EtatPatient.SOINS_CRITIQUES, Localisation.SOINS_CRITIQUES, "Direct IOA -> Soins Critiques")
            elif p.gravite == Gravite.VERT and self.hospital.ressources.medecin_disponible:
                p.transition_to(EtatPatient.EN_CONSULTATION, Localisation.CONSULTATION, "Direct IOA -> Consultation")
            else:
                # Tentative SA par défaut ou logique spécifique
                for sa_loc in [Localisation.SA3, Localisation.SA2, Localisation.SA1]:
                    if peut_entrer_en_sa(sa_loc, self.hospital.ressources):
                        self.hospital.ressources.modifier_occupation_sa(sa_loc, 1)
                        p.transition_to(EtatPatient.EN_ATTENTE, sa_loc, f"IOA -> {sa_loc.value}")
                        break

        # 2. Flux Stagnation SA -> Unités
        for p in [p for p in self.hospital.patients.values() if p.etat_courant == EtatPatient.ATTENTE_TRANSFERT]:
            if peut_aller_en_unite(p, self.hospital.ressources):
                self.hospital.ressources.modifier_occupation_sa(p.localisation_courante, -1)
                self.hospital.ressources.unites[p.specialite_requise].patients_presents += 1
                p.transition_to(EtatPatient.EN_UNITE, Localisation.UNITE, "SA -> Hôpital (Lit libéré)")

    def simuler_orientation(self, patient_id: str, hospitalisation: bool):
        p = self.hospital.patients[patient_id]
        # Libération de la zone de soin
        if p.localisation_courante == Localisation.CONSULTATION:
            pass # Libère médecin si besoin
            
        if hospitalisation:
            # Règle schéma : Orientation -> SA (Stagnation)
            for sa_loc in [Localisation.SA2, Localisation.SA3, Localisation.SA1]:
                if peut_entrer_en_sa(sa_loc, self.hospital.ressources):
                    self.hospital.ressources.modifier_occupation_sa(sa_loc, 1)
                    p.transition_to(EtatPatient.ATTENTE_TRANSFERT, sa_loc, "Besoin Hospitalisation -> SA")
                    break
        else:
            p.transition_to(EtatPatient.SORTI, Localisation.EXTERIEUR, "Orientation -> SORTIE")
