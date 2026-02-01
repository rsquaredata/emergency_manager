class EtatPatient(Enum):
    ARRIVE = "ARRIVÉ"
    EN_ATTENTE = "EN_ATTENTE" # Dans l'une des 3 SA
    EN_CONSULTATION = "ZONE_CONSULTATION"
    SOINS_CRITIQUES = "SOINS_CRITIQUES" # Nouveau bloc
    EN_ATTENTE_TRANSFERT = "ATTENTE_TRANSFERT" # Retour en SA
    EN_UNITE = "HÔPITAL_UNITE"
    SORTI = "SORTIE" # Libellé unique
