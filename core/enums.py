from __future__ import annotations

from enum import Enum


class SeverityLevel(str, Enum):
    GRIS = "GRIS"
    VERT = "VERT"
    JAUNE = "JAUNE"
    ROUGE = "ROUGE"


class PatientState(str, Enum):
    ARRIVED = "ARRIVED"
    WAITING = "WAITING"
    IN_CONSULTATION = "IN_CONSULTATION"
    IN_EXAM = "IN_EXAM"
    AWAITING_TRANSFER = "AWAITING_TRANSFER"
    IN_UNIT = "IN_UNIT"
    DISCHARGED = "DISCHARGED"
    LEFT = "LEFT"  # e.g., GRIS redirection


class Location(str, Enum):
    TRIAGE = "TRIAGE"
    WAITING_AREA = "WAITING_AREA"
    CONSULTATION_ROOM = "CONSULTATION_ROOM"
    EXAM_AREA = "EXAM_AREA"
    TRANSFER_QUEUE = "TRANSFER_QUEUE"
    HOSPITAL_UNIT = "HOSPITAL_UNIT"
    EXIT = "EXIT"
