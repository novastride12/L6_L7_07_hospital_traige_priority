import pytest

from hospital_triage_priority import (
    process_triage_wards,
    monitor_oxygen_manifolds,
)


def test_valid_and_invalid_wards():
    with pytest.raises(ValueError):
        process_triage_wards("invalid", 10)

    with pytest.raises(ValueError):
        process_triage_wards([], -1)


def test_ward_accepting_and_not_accepting():
    wards = [
        {"is_accepting": False},
        {
            "is_accepting": True,
            "patients": [{"spo2": 98, "hr": 75}],
        },
    ]

    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


def test_patient_invalid_spo2_and_heart_rate():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": 0, "hr": 75},
            {"spo2": 95, "hr": 0},
            {"spo2": 95, "hr": 75},
        ],
    }]

    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


def test_unconscious_general_and_outpatient():
    general = [{
        "is_accepting": True,
        "tier": "general",
        "patients": [{"unconscious": True}],
    }]

    outpatient = [{
        "is_accepting": True,
        "tier": "outpatient",
        "patients": [{"unconscious": True}],
    }]

    assert process_triage_wards(general, 10)["acuity_score"] == 100
    assert process_triage_wards(outpatient, 10)["acuity_score"] == 0


def test_low_spo2_and_high_heart_rate_branches():
    low_spo2 = [{
        "is_accepting": True,
        "patients": [{"spo2": 85, "hr": 75}],
    }]

    high_hr = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 130}],
    }]

    normal = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 75}],
    }]

    assert process_triage_wards(low_spo2, 10)["acuity_score"] == 60
    assert process_triage_wards(high_hr, 10)["acuity_score"] == 60
    assert process_triage_wards(normal, 10)["acuity_score"] == 10


def test_icu_standby_true_and_false():
    with_icu = [{
        "is_accepting": True,
        "icu_standby": True,
        "patients": [],
    }]

    without_icu = [{
        "is_accepting": True,
        "icu_standby": False,
        "patients": [],
    }]

    assert process_triage_wards(with_icu, 10)["acuity_score"] == 25
    assert process_triage_wards(without_icu, 10)["acuity_score"] == 0


def test_ward_alert_threshold():
    four_flagged = [{
        "is_accepting": True,
        "patients": [{"spo2": 0} for _ in range(4)],
    }]

    five_flagged = [{
        "is_accepting": True,
        "patients": [{"spo2": 0} for _ in range(5)],
    }]

    assert process_triage_wards(four_flagged, 10)["status"] == "NO_URGENT_CASES"
    assert process_triage_wards(five_flagged, 10)["status"] == "WARD_ALERT"


def test_oxygen_pressure_branches():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"

    assert monitor_oxygen_manifolds([[5.0, 4.0]]) == "PRESSURE_NORMAL"
    assert monitor_oxygen_manifolds([[3.5, 3.0]]) == "PRESSURE_FAILURE"
    assert monitor_oxygen_manifolds([[3.0, 5.0, 3.0]]) == "PRESSURE_NORMAL"