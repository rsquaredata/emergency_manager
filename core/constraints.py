from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.enums import PatientState
from core.patient import Patient
from core.resources import ConsultationRoom, HospitalUnit


@dataclass(slots=True)
class ConstraintViolation:
    rule: str
    message: str


class Constraints:
    """
    Hard constraints (must never be violated).
    """

    @staticmethod
    def must_see_doctor_before_transfer(patient: Patient) -> Optional[ConstraintViolation]:
        # Simplified proxy: if patient hasn't been in consultation, no transfer.
        # TODO: In a later iteration, we can make this explicit via events/flags.
        has_seen_doctor = any(
            old == PatientState.IN_CONSULTATION or new == PatientState.IN_CONSULTATION
            for _, old, new, _ in patient.history
        ) or (patient.state == PatientState.IN_CONSULTATION)

        if not has_seen_doctor and patient.state == PatientState.AWAITING_TRANSFER:
            return ConstraintViolation(
                rule="must_see_doctor_before_transfer",
                message="Patient cannot await transfer without prior consultation.",
            )
        return None

    @staticmethod
    def unit_must_have_capacity(unit: HospitalUnit) -> Optional[ConstraintViolation]:
        if not unit.has_capacity():
            return ConstraintViolation(
                rule="unit_must_have_capacity",
                message=f"Unit {unit.unit_id} has no available capacity.",
            )
        return None

    @staticmethod
    def room_requires_supervising_doctor(room: ConsultationRoom) -> Optional[ConstraintViolation]:
        if room.supervising_doctor_id is None:
            return ConstraintViolation(
                rule="room_requires_supervising_doctor",
                message=f"Room {room.room_id} has no supervising doctor.",
            )
        return None

