from enum import IntEnum, Enum

class Gravite(IntEnum):
    GRIS = 0
    VERT = 1
    JAUNE = 2
    ROUGE = 3

class EtatPatient(Enum):
    ARRIVE = "ARRIVÉ"
    EN_ATTENTE = "EN_ATTENTE"
    EN_CONSULTATION = "EN_CONSULTATION"
    EN_EXAMEN = "EN_EXAMEN"
    EN_ATTENTE_TRANSFERT = "EN_ATTENTE_TRANSFERT"
    EN_UNITE = "EN_UNITÉ"
    SORTI = "SORTI"
    ORIENTE_EXTERIEUR = "ORIENTÉ_EXTÉRIEUR"

class Specialite(Enum):
    CARDIOLOGIE = "Cardiologie"
    NEUROLOGIE = "Neurologie"
    PNEUMOLOGIE = "Pneumologie"
    ORTHOPEDIE = "Orthopédie"
    AUCUNE = "Aucune"
