from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from core.enums import SeverityLevel, PatientState, Location
from core.patient import Patient
from core.hospital import EmergencyDepartmentState
from core.constraints import Constraints, ConstraintViolation


class SchedulerDecisionError(Exception):
    """Raised when no valid scheduling decision can be made."""
    pass


class BaselineScheduler:
    """
    Deterministic, rule-based scheduler for the emergency department.

    This scheduler:
    - applies hard constraints strictly,
    - prioritizes patients by severity and waiting time,
    - does NOT use any AI or probabilistic logic.

    It defines the reference behavior of the system.
    """

    def __init__(self, ed_state: EmergencyDepartmentState):
        self.ed_state = ed_state

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def step(self) -> None:
        """
        Execute one scheduling step.

        A step consists of:
        - redirecting GRIS patients,
        - attempting to move eligible patients forward in the system,
        - respecting all hard constraints.

        If no valid action is possible, the system remains unchanged.
        """
        self._redirect_gris_patients()

        # Process patients by priority order
        for patient in self._prioritized_patients():
            if self._try_progress_patient(patient):
                # Only one patient is progressed per step
                return

    # ---------------------------------------------------------------------
    # Priority logic
    # ---------------------------------------------------------------------

    def _prioritized_patients(self) -> List[Patient]:
        """
        Return active patients ordered by priority:
        1. Severity (ROUGE > JAUNE > VERT)
        2. Waiting time (descending)
        """
        severity_rank = {
            SeverityLevel.ROUGE: 3,
            SeverityLevel.JAUNE: 2,
            SeverityLevel.VERT: 1,
            SeverityLevel.GRIS: 0,
        }

        patients = [
            p for p in self.ed_state.active_patients()
            if p.severity != SeverityLevel.GRIS
        ]

        return sorted(
            patients,
            key=lambda p: (
                severity_rank[p.severity],
                p.waiting_time_minutes,
            ),
            reverse=True,
        )

    # ---------------------------------------------------------------------
    # Core progression logic
    # ---------------------------------------------------------------------

    def _try_progress_patient(self, patient: Patient) -> bool:
        """
        Attempt to move a patient to the next valid state.

        Returns True if a transition was performed, False otherwise.
        """
        if patient.state == PatientState.WAITING:
            return self._try_assign_to_consultation(patient)

        if patient.state == PatientState.IN_CONSULTATION:
            return self._try_post_consultation(patient)

        if patient.state == PatientState.AWAITING_TRANSFER:
            return self._try_transfer_to_unit(patient)

        return False

    # ---------------------------------------------------------------------
    # Specific transitions
    # ---------------------------------------------------------------------

    def _redirect_gris_patients(self) -> None:
        """
        Immediately redirect GRIS patients outside the emergency department.
        """
        now = self.ed_state.now
        for patient in self.ed_state.active_patients():
            if patient.severity == SeverityLevel.GRIS:
                patient.transition_to(
                    new_state=PatientState.LEFT,
                    new_location=Location.EXIT,
                    now=now,
                    reason="GRIS severity: redirected outside emergency department",
                )

    def _try_assign_to_consultation(self, patient: Patient) -> bool:
        """
        Try to assign a waiting patient to a consultation room.
        """
        now = self.ed_state.now

        available_rooms = [
            room for room in self.ed_state.resources.rooms.values()
            if room.can_accept_patient()
        ]

        if not available_rooms:
            return False

        room = available_rooms[0]

        room.admit_patient(patient.patient_id)

        patient.transition_to(
            new_state=PatientState.IN_CONSULTATION,
            new_location=Location.CONSULTATION_ROOM,
            now=now,
            reason=f"Assigned to consultation room {room.room_id}",
        )

        return True

    def _try_post_consultation(self, patient: Patient) -> bool:
        """
        Decide what happens after consultation.

        Baseline logic:
        - ROUGE / JAUNE → attempt transfer
        - VERT → discharge
        """
        now = self.ed_state.now

        if patient.severity in {SeverityLevel.ROUGE, SeverityLevel.JAUNE}:
            patient.transition_to(
                new_state=PatientState.AWAITING_TRANSFER,
                new_location=Location.TRANSFER_QUEUE,
                now=now,
                reason="Post-consultation: transfer required",
            )
            return True

        if patient.severity == SeverityLevel.VERT:
            patient.transition_to(
                new_state=PatientState.DISCHARGED,
                new_location=Location.EXIT,
                now=now,
                reason="Post-consultation: discharged (VERT)",
            )
            return True

        return False

    def _try_transfer_to_unit(self, patient: Patient) -> bool:
        """
        Attempt to transfer a patient to a hospital unit.
        """
        now = self.ed_state.now

        # Constraint: must have seen a doctor
        violation = Constraints.must_see_doctor_before_transfer(patient)
        if violation:
            return False

        # Select compatible units
        candidate_units = [
            unit for unit in self.ed_state.resources.units.values()
            if unit.has_capacity()
        ]

        if not candidate_units:
            return False

        unit = candidate_units[0]

        unit.admit()

        patient.transition_to(
            new_state=PatientState.IN_UNIT,
            new_location=Location.HOSPITAL_UNIT,
            now=now,
            reason=f"Transferred to unit {unit.unit_id}",
        )

        return True

