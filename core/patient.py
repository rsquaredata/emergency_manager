from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Tuple

from core.enums import SeverityLevel, PatientState, Location


Transition = Tuple[datetime, PatientState, PatientState, str]


@dataclass(slots=True)
class Patient:
    """
    Core patient entity.

    This class is part of the deterministic (no-AI) system model.
    It tracks severity, current state, location, and a transition history.
    """

    patient_id: str
    severity: SeverityLevel
    arrival_time: datetime

    state: PatientState = PatientState.ARRIVED
    location: Location = Location.TRIAGE

    required_specialty: Optional[str] = None  # e.g., "cardiology"
    waiting_time_minutes: float = 0.0

    history: List[Transition] = field(default_factory=list)

    def transition_to(
        self,
        new_state: PatientState,
        new_location: Location,
        now: datetime,
        reason: str,
    ) -> None:
        """Record a state transition with a human-readable reason."""
        old_state = self.state
        self.state = new_state
        self.location = new_location
        self.history.append((now, old_state, new_state, reason))

    def is_active(self) -> bool:
        """Active patients are those not discharged/left."""
        return self.state not in {PatientState.DISCHARGED, PatientState.LEFT}

