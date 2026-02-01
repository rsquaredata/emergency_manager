from datetime import datetime

import pytest

from core.enums import SeverityLevel, PatientState, Location
from core.patient import Patient
from core.resources import (
    StaffMember,
    ConsultationRoom,
    HospitalUnit,
    ResourcePool,
)
from core.hospital import EmergencyDepartmentState
from core.scheduler import BaselineScheduler


# ---------------------------------------------------------------------
# Fixtures utilitaires
# ---------------------------------------------------------------------

@pytest.fixture
def now() -> datetime:
    return datetime(2026, 1, 1, 8, 0, 0)


def make_basic_ed_state(now: datetime) -> EmergencyDepartmentState:
    """
    Create a minimal emergency department state with:
    - 1 doctor
    - 1 consultation room
    - 1 hospital unit (capacity 1)
    """
    doctor = StaffMember(staff_id="doc_1", role="doctor")
    room = ConsultationRoom(room_id="room_1")
    room.assign_doctor(doctor.staff_id)

    unit = HospitalUnit(
        unit_id="unit_1",
        specialty="general",
        capacity=1,
    )

    resources = ResourcePool(
        staff={doctor.staff_id: doctor},
        rooms={room.room_id: room},
        units={unit.unit_id: unit},
    )

    return EmergencyDepartmentState(
        now=now,
        resources=resources,
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_gris_patient_is_redirected_immediately(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.GRIS,
        arrival_time=now,
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.LEFT
    assert patient.location == Location.EXIT


def test_rouge_patient_has_priority_over_vert(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    rouge = Patient(
        patient_id="p_rouge",
        severity=SeverityLevel.ROUGE,
        arrival_time=now,
        state=PatientState.WAITING,
        location=Location.WAITING_AREA,
    )

    vert = Patient(
        patient_id="p_vert",
        severity=SeverityLevel.VERT,
        arrival_time=now,
        state=PatientState.WAITING,
        location=Location.WAITING_AREA,
    )

    ed_state.add_patient(rouge)
    ed_state.add_patient(vert)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert rouge.state == PatientState.IN_CONSULTATION
    assert vert.state == PatientState.WAITING


def test_waiting_patient_moves_to_consultation_when_room_available(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.JAUNE,
        arrival_time=now,
        state=PatientState.WAITING,
        location=Location.WAITING_AREA,
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.IN_CONSULTATION
    assert patient.location == Location.CONSULTATION_ROOM


def test_vert_patient_is_discharged_after_consultation(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.VERT,
        arrival_time=now,
        state=PatientState.IN_CONSULTATION,
        location=Location.CONSULTATION_ROOM,
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.DISCHARGED
    assert patient.location == Location.EXIT


def test_rouge_patient_moves_to_transfer_after_consultation(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.ROUGE,
        arrival_time=now,
        state=PatientState.IN_CONSULTATION,
        location=Location.CONSULTATION_ROOM,
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.AWAITING_TRANSFER
    assert patient.location == Location.TRANSFER_QUEUE


def test_patient_is_transferred_to_unit_if_capacity_available(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.ROUGE,
        arrival_time=now,
        state=PatientState.AWAITING_TRANSFER,
        location=Location.TRANSFER_QUEUE,
    )

    # Simulate prior consultation
    patient.history.append(
        (now, PatientState.WAITING, PatientState.IN_CONSULTATION, "consulted")
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.IN_UNIT
    assert patient.location == Location.HOSPITAL_UNIT

    unit = next(iter(ed_state.resources.units.values()))
    assert unit.occupancy == 1


def test_patient_not_transferred_if_no_unit_capacity(now: datetime) -> None:
    ed_state = make_basic_ed_state(now)

    unit = next(iter(ed_state.resources.units.values()))
    unit.occupancy = unit.capacity  # saturate unit

    patient = Patient(
        patient_id="p1",
        severity=SeverityLevel.ROUGE,
        arrival_time=now,
        state=PatientState.AWAITING_TRANSFER,
        location=Location.TRANSFER_QUEUE,
    )

    patient.history.append(
        (now, PatientState.WAITING, PatientState.IN_CONSULTATION, "consulted")
    )

    ed_state.add_patient(patient)

    scheduler = BaselineScheduler(ed_state)
    scheduler.step()

    assert patient.state == PatientState.AWAITING_TRANSFER
    assert patient.location == Location.TRANSFER_QUEUE
