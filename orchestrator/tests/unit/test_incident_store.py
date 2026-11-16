import sqlite3
from datetime import datetime

import pytest

from orchestrator.app.integrations.incident_store import IncidentStore


@pytest.fixture
def incident_store(tmp_path):
    database_path = tmp_path / "nested" / "incidents.db"
    store = IncidentStore(database_path)
    store.initialize()
    return store


def test_initialize_creates_database_and_table(tmp_path):
    database_path = tmp_path / "nested" / "incidents.db"
    store = IncidentStore(database_path)

    store.initialize()

    assert database_path.exists()

    with sqlite3.connect(database_path) as connection:
        result = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='incidents'"
        ).fetchone()

    assert result is not None


def test_initialize_preserves_existing_records(incident_store):
    created = incident_store.create_incident(
        namespace="default",
        resource_type="Deployment",
        resource_name="frontend",
        trigger="high_cpu",
        status="detected",
    )

    incident_store.initialize()

    result = incident_store.get_incident(created["id"])

    assert result is not None
    assert result["resource_name"] == "frontend"


def test_create_incident_returns_saved_record(incident_store):
    details = {"cpu_usage": 95.5}

    incident = incident_store.create_incident(
        namespace="default",
        resource_type="Deployment",
        resource_name="frontend",
        trigger="high_cpu",
        status="detected",
        diagnosis="CPU usage is high",
        action="restart",
        details=details,
    )

    assert incident["id"] is not None
    assert incident["namespace"] == "default"
    assert incident["resource_name"] == "frontend"
    assert incident["details"] == details
    assert incident["diagnosis"] == "CPU usage is high"
    assert incident["action"] == "restart"

    # Verify that the timestamp is valid ISO 8601.
    datetime.fromisoformat(incident["created_at"])


def test_list_incidents_returns_newest_first(incident_store):
    first = incident_store.create_incident(
        namespace="default",
        resource_type="Deployment",
        resource_name="frontend",
        trigger="high_cpu",
        status="detected",
    )

    second = incident_store.create_incident(
        namespace="default",
        resource_type="Deployment",
        resource_name="cartservice",
        trigger="pod_failure",
        status="detected",
    )

    incidents = incident_store.list_incidents()

    assert len(incidents) == 2
    assert incidents[0]["id"] == second["id"]
    assert incidents[1]["id"] == first["id"]


def test_list_incidents_supports_pagination(incident_store):
    for name in ["frontend", "cartservice", "emailservice"]:
        incident_store.create_incident(
            namespace="default",
            resource_type="Deployment",
            resource_name=name,
            trigger="test",
            status="detected",
        )

    incidents = incident_store.list_incidents(limit=1, offset=1)

    assert len(incidents) == 1
    assert incidents[0]["resource_name"] == "cartservice"


def test_get_incident_returns_none_for_missing_id(incident_store):
    result = incident_store.get_incident(999)

    assert result is None


def test_incident_with_no_details(incident_store):
    incident = incident_store.create_incident(
        namespace="default",
        resource_type="Deployment",
        resource_name="frontend",
        trigger="high_cpu",
        status="detected",
    )

    result = incident_store.get_incident(incident["id"])

    assert result is not None
    assert result["details"] is None
