from enum import IntEnum, Enum

class Gravite(IntEnum):
    GRIS = 0
    VERT = 1
    JAUNE = 2
    ROUGE = 3

class EtatPatient(Enum):
    ARRIVE = "ARRIVÉ"
    EN_ATTENTE = "EN_ATTENTE"  # Dans une des 3 Salles d'Attente
    EN_CONSULTATION = "ZONE_CONSULTATION"
    SOINS_CRITIQUES = "SOINS_CRITIQUES"
    ATTENTE_TRANSFERT = "ATTENTE_TRANSFERT" # Cas de stagnation en SA
    EN_UNITE = "HÔPITAL_UNITE"
    SORTI = "SORTIE"

class Localisation(Enum):
    SA1 = "SA1"
    SA2 = "SA2"
    SA3 = "SA3"
    CONSULTATION = "Consultation"
    SOINS_CRITIQUES = "Soins Critiques"
    UNITE = "Unité Hospitalière"
    EXTERIEUR = "Extérieur"

class Specialite(Enum):
    CARDIOLOGIE = "Cardiologie"
    NEUROLOGIE = "Neurologie"
    PNEUMOLOGIE = "Pneumologie"
    ORTHOPEDIE = "Orthopédie"
    AUCUNE = "Aucune"
