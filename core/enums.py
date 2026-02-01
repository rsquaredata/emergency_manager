from enum import IntEnum, Enum


class Gravite(IntEnum):
    GRIS = 0      # Orientation externe
    VERT = 1      # Non urgent
    JAUNE = 2     # Urgent non vital
    ROUGE = 3     # Urgence vitale


class EtatPatient(Enum):
    ARRIVE = "ARRIVE"

    EN_ATTENTE = "EN_ATTENTE"                # Salle d'attente (SA1, SA2, SA3)
    EN_CONSULTATION = "EN_CONSULTATION"      # Consultation médicale
    EN_EXAMEN = "EN_EXAMEN"                  # Examens complémentaires

    SOINS_CRITIQUES = "SOINS_CRITIQUES"      # Urgence vitale directe

    ATTENTE_TRANSFERT = "ATTENTE_TRANSFERT"  # Décision d'hospitalisation prise, lit indisponible
    EN_UNITE = "EN_UNITE"                    # Hospitalisation effective

    ORIENTE_EXTERIEUR = "ORIENTE_EXTERIEUR"  # Cas GRIS
    SORTI = "SORTI"


class Localisation(Enum):
    SA1 = "SA1"
    SA2 = "SA2"
    SA3 = "SA3"

    CONSULTATION = "CONSULTATION"
    EXAMEN = "EXAMEN"
    SOINS_CRITIQUES = "SOINS_CRITIQUES"

    UNITE = "UNITE"
    EXTERIEUR = "EXTERIEUR"


class Specialite(Enum):
    CARDIOLOGIE = "CARDIOLOGIE"
    NEUROLOGIE = "NEUROLOGIE"
    PNEUMOLOGIE = "PNEUMOLOGIE"
    ORTHOPEDIE = "ORTHOPEDIE"
    AUCUNE = "AUCUNE"
