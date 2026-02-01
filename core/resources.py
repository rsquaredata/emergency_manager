from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass(slots=True)
class StaffMember:
    """
    Human resource model (doctor, nurse, nurse assistant).
    """

    staff_id: str
    role: str  # "doctor" | "nurse" | "assistant"
    available: bool = True
    assigned_to: Optional[str] = None  # room_id / patient_id / task_id

    def assign(self, target_id: str) -> None:
        self.available = False
        self.assigned_to = target_id

    def release(self) -> None:
        self.available = True
        self.assigned_to = None


@dataclass(slots=True)
class ConsultationRoom:
    """
    Physical resource: consultation room.
    A room is usable only if a supervising doctor is assigned.
    """

    room_id: str
    available: bool = True
    supervising_doctor_id: Optional[str] = None
    current_patient_id: Optional[str] = None

    def can_accept_patient(self) -> bool:
        return self.available and self.supervising_doctor_id is not None

    def assign_doctor(self, doctor_id: str) -> None:
        self.supervising_doctor_id = doctor_id

    def admit_patient(self, patient_id: str) -> None:
        if not self.can_accept_patient():
            raise ValueError("Room cannot accept patient: missing doctor or not available.")
        self.available = False
        self.current_patient_id = patient_id

    def discharge_patient(self) -> None:
        self.available = True
        self.current_patient_id = None


@dataclass(slots=True)
class HospitalUnit:
    """
    Downstream unit with limited capacity (e.g., cardiology, critical care).
    """

    unit_id: str
    specialty: str  # e.g., "cardiology"
    capacity: int
    occupancy: int = 0

    def has_capacity(self) -> bool:
        return self.occupancy < self.capacity

    def admit(self) -> None:
        if not self.has_capacity():
            raise ValueError("Unit has no available capacity.")
        self.occupancy += 1

    def release(self) -> None:
        if self.occupancy <= 0:
            raise ValueError("Invalid release: occupancy already zero.")
        self.occupancy -= 1


@dataclass(slots=True)
class ResourcePool:
    """
    Container for all resources.
    """

    staff: Dict[str, StaffMember] = field(default_factory=dict)
    rooms: Dict[str, ConsultationRoom] = field(default_factory=dict)
    units: Dict[str, HospitalUnit] = field(default_factory=dict)

    def available_doctors(self) -> list[StaffMember]:
        return [s for s in self.staff.values() if s.role == "doctor" and s.available]

    def available_nurses(self) -> list[StaffMember]:
        return [s for s in self.staff.values() if s.role == "nurse" and s.available]

    def available_assistants(self) -> list[StaffMember]:
        return [s for s in self.staff.values() if s.role == "assistant" and s.available]

