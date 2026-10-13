"""Regressions for previously misleading configuration and unsafe API behavior."""
import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.llm_factory import LLMFactory
from agents.models import SystemTaskPayload


def test_external_providers_are_not_silently_mocked():
    for name in ("openai", "claude", "ollama", "unknown"):
        with pytest.raises(ValueError, match="not implemented"):
            LLMFactory.create(name)


def test_mock_does_not_claim_clinical_validation():
    reply = LLMFactory.create("mock").invoke("Check system")
    assert "no clinical assertions were verified" in reply


def test_post_sanitization_blank_identifier_rejected():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="\n\t", target_identifier="SYNTH", primary_metric=10)


def test_nonfinite_metric_rejected():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T", target_identifier="SYNTH", primary_metric=float("nan"))


def test_phi_in_api_returns_422_instead_of_server_error():
    response = TestClient(app).post("/api/audit", json={
        "task_id": "MRN-1234567",
        "target_identifier": "SYNTH",
        "primary_metric": 15
    })
    assert response.status_code == 422


def test_metrics_report_running_not_unverified_optimal():
    response = TestClient(app).get("/metrics")
    assert response.status_code == 200
    assert response.json()["system_status"] == "RUNNING"
