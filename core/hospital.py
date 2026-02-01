from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from core.patient import Patient
from core.resources import ResourcePool


@dataclass(slots=True)
class EmergencyDepartmentState:
    """
    Global state: single source of truth.

    Holds active patients, resources, and the current simulation time.
    """

    now: datetime
    patients: Dict[str, Patient] = field(default_factory=dict)
    resources: ResourcePool = field(default_factory=ResourcePool)

    def add_patient(self, patient: Patient) -> None:
        if patient.patient_id in self.patients:
            raise ValueError(f"Patient already exists: {patient.patient_id}")
        self.patients[patient.patient_id] = patient

    def get_patient(self, patient_id: str) -> Patient:
        return self.patients[patient_id]

    def active_patients(self) -> List[Patient]:
        return [p for p in self.patients.values() if p.is_active()]

    def advance_time(self, new_now: datetime) -> None:
        if new_now < self.now:
            raise ValueError("Cannot go back in time.")
        self.now = new_now

