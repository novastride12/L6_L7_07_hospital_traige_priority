
import pytest

from hospital_triage_priority import (
    process_triage_wards,
    monitor_oxygen_manifolds,
)


def test_invalid_wards_type():
    with pytest.raises(ValueError):
        process_triage_wards("invalid", 10)


def test_negative_acuity():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


def test_empty_wards():
    result = process_triage_wards([], 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_non_accepting_ward():
    wards = [{"is_accepting": False}]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_normal_patient():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 98, "hr": 75}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10
    assert result["status"] == "TRIAGE_STABLE"


def test_invalid_spo2():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0, "hr": 75}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_invalid_heart_rate():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 0}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_unconscious_general_patient():
    wards = [{
        "is_accepting": True,
        "tier": "general",
        "patients": [{"unconscious": True}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 100


def test_unconscious_outpatient():
    wards = [{
        "is_accepting": True,
        "tier": "outpatient",
        "patients": [{"unconscious": True}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_low_spo2():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 85, "hr": 75}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_high_heart_rate():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 130}]
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_icu_standby():
    wards = [{
        "is_accepting": True,
        "icu_standby": True,
        "patients": []
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 25


def test_ward_alert():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0} for _ in range(5)]
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"


def test_no_oxygen_data():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


def test_normal_oxygen_pressure():
    assert monitor_oxygen_manifolds(
        [[5.0, 4.5, 4.0]]
    ) == "PRESSURE_NORMAL"


def test_oxygen_pressure_failure():
    assert monitor_oxygen_manifolds(
        [[3.5, 3.0]]
    ) == "PRESSURE_FAILURE"


def test_pressure_recovers():
    assert monitor_oxygen_manifolds(
        [[3.0, 5.0, 3.0]]
    ) == "PRESSURE_NORMAL"
