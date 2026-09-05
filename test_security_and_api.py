"""
Security, API, and agents package tests for hypertensive-crisis-agent.
"""
import os
import warnings
import pytest
from agents.base import (
    assert_no_phi,
    PHIGuard,
    AuditTrail,
    AuditLogger,
    SecurityException,
    GLOBAL_AUDIT,
)
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.supervisor import SystemSupervisor
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker


# ==============================================================================
# SECURITY / PHI GUARD TESTS
# ==============================================================================

class TestPHIGuard:
    def test_clean_text_passes(self):
        """Non-PHI text should not raise."""
        assert_no_phi("Normal clinical observation with no identifiers.")

    def test_mrn_detected(self):
        """MRN pattern should raise SecurityException."""
        with pytest.raises(SecurityException):
            assert_no_phi("Patient MRN-12345678 admitted.")

    def test_ssn_detected(self):
        """SSN pattern should raise SecurityException."""
        with pytest.raises(SecurityException):
            assert_no_phi("SSN: 123-45-6789")

    def test_phone_detected(self):
        """Phone number pattern should raise SecurityException."""
        with pytest.raises(SecurityException):
            assert_no_phi("Call patient at 555-123-4567")

    def test_email_detected(self):
        """Email pattern should raise SecurityException."""
        with pytest.raises(SecurityException):
            assert_no_phi("Email: patient@example.com")

    def test_john_doe_detected(self):
        """Common placeholder names should raise SecurityException."""
        with pytest.raises(SecurityException):
            assert_no_phi("Patient John Doe discharged.")

    def test_redact_phi(self):
        """PHI redaction should replace identifiers."""
        redacted = PHIGuard.redact_phi("MRN-12345678 and 123-45-6789")
        assert "REDACTED_IDENTIFIER" in redacted
        assert "12345678" not in redacted
        assert "123-45-6789" not in redacted

    def test_empty_text_no_error(self):
        """Empty or None text should not raise."""
        assert_no_phi("")
        assert_no_phi(None)


# ==============================================================================
# AUDIT TRAIL TESTS
# ==============================================================================

class TestAuditTrail:
    def test_audit_trail_chaining(self):
        """Audit entries should form a proper chain."""
        trail = AuditTrail(secret_key="test-key-123")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"key": "value"})
        trail.log("test_actor", "test_tier", "TEST_EVENT_2", {"key2": "value2"})
        assert len(trail.get_trail()) == 2
        assert trail.verify_integrity() is True

    def test_audit_tamper_detection(self):
        """Tampered audit trail should fail verification."""
        trail = AuditTrail(secret_key="test-key-456")
        trail.log("actor", "tier", "EVENT", {"data": "original"})
        # Tamper with the first entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False

    def test_audit_prevents_phi_in_logs(self):
        """Audit log should reject PHI-containing details."""
        trail = AuditTrail(secret_key="test-key-789")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"patient": "John Doe"})

    def test_audit_generates_unique_ids(self):
        """Each audit entry should have a unique ID."""
        trail = AuditTrail(secret_key="test-key-unique")
        e1 = trail.log("a", "t", "E1", {"x": 1})
        e2 = trail.log("a", "t", "E2", {"x": 2})
        assert e1["audit_id"] != e2["audit_id"]

    def test_ephemeral_key_warning(self):
        """Missing AUDIT_SECRET_KEY should produce a warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            assert len(w) == 1
            assert "AUDIT_SECRET_KEY" in str(w[0].message)


# ==============================================================================
# INPUT VALIDATION TESTS
# ==============================================================================

class TestInputValidation:
    def test_valid_payload(self):
        """Valid payload should be accepted."""
        p = SystemTaskPayload(
            task_id="TASK-001",
            target_identifier="TARGET-001",
            primary_metric=25.0,
            secondary_metric=10.0,
        )
        assert p.task_id == "TASK-001"
        assert p.primary_metric == 25.0

    def test_empty_task_id_rejected(self):
        """Empty task_id should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="", target_identifier="T", primary_metric=10.0)

    def test_negative_metric_rejected(self):
        """Negative metrics should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="T", target_identifier="T", primary_metric=-5.0)

    def test_metric_upper_bound(self):
        """Metrics exceeding upper bound should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="T", target_identifier="T", primary_metric=5000.0)

    def test_long_task_id_rejected(self):
        """Overly long task_id should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="X" * 200, target_identifier="T", primary_metric=10.0)

    def test_text_sanitization(self):
        """Control characters should be stripped from text fields."""
        p = SystemTaskPayload(
            task_id="  TASK-001  ",
            target_identifier="TARGET\n001",
            primary_metric=10.0,
        )
        assert p.task_id == "TASK-001"
        assert "\n" not in p.target_identifier


# ==============================================================================
# WORKER TESTS
# ==============================================================================

class TestWorkers:
    def test_qc_worker_normal(self):
        """QC worker should not alert for normal values."""
        p = SystemTaskPayload(task_id="T", target_identifier="T", primary_metric=15.0)
        alerts = InvariantQCWorker.evaluate(p)
        assert len(alerts) == 0

    def test_qc_worker_threshold_exceeded(self):
        """QC worker should alert when primary metric exceeds 25."""
        p = SystemTaskPayload(task_id="T", target_identifier="T", primary_metric=35.0)
        alerts = InvariantQCWorker.evaluate(p)
        assert len(alerts) == 1
        assert alerts[0].urgency == UrgencyLevel.ELEVATED

    def test_safety_worker_critical(self):
        """Safety worker should CRITICAL_STAT when is_critical_flag is True."""
        p = SystemTaskPayload(task_id="T", target_identifier="T", primary_metric=10.0, is_critical_flag=True)
        alerts = SafetyEscalationWorker.evaluate(p)
        assert len(alerts) == 1
        assert alerts[0].urgency == UrgencyLevel.CRITICAL_STAT

    def test_safety_worker_secondary_threshold(self):
        """Safety worker should alert when secondary metric exceeds 12."""
        p = SystemTaskPayload(
            task_id="T", target_identifier="T",
            primary_metric=10.0, secondary_metric=15.0
        )
        alerts = SafetyEscalationWorker.evaluate(p)
        assert len(alerts) == 1
        assert alerts[0].urgency == UrgencyLevel.ELEVATED

    def test_conformance_worker_discordant(self):
        """Conformance worker should alert on discordant descriptors."""
        p = SystemTaskPayload(
            task_id="T", target_identifier="T",
            primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY"
        )
        alerts = ProtocolConformanceWorker.evaluate(p)
        assert len(alerts) == 1

    def test_conformance_worker_normal(self):
        """Conformance worker should not alert on normal descriptors."""
        p = SystemTaskPayload(
            task_id="T", target_identifier="T",
            primary_metric=10.0, status_descriptor="NOMINAL"
        )
        alerts = ProtocolConformanceWorker.evaluate(p)
        assert len(alerts) == 0


# ==============================================================================
# SUPERVISOR TESTS
# ==============================================================================

class TestSupervisor:
    def test_process_task_routine(self):
        """Supervisor should return ROUTINE for normal payload."""
        sup = SystemSupervisor(model_provider="mock")
        p = SystemTaskPayload(
            task_id="TASK-NORMAL", target_identifier="TARGET-01",
            primary_metric=15.0, secondary_metric=5.0,
            status_descriptor="NOMINAL"
        )
        dossier = sup.process_task(p)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE
        assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED

    def test_process_task_critical(self):
        """Supervisor should return CRITICAL_STAT for critical payload."""
        sup = SystemSupervisor(model_provider="mock")
        p = SystemTaskPayload(
            task_id="TASK-CRIT", target_identifier="TARGET-01",
            primary_metric=35.0, secondary_metric=15.0,
            is_critical_flag=True
        )
        dossier = sup.process_task(p)
        assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT
        assert dossier.integrity_status == SystemIntegrityStatus.RECALIBRATION_REQUIRED

    def test_supervisor_stores_dossier(self):
        """Supervisor should store processed dossiers."""
        sup = SystemSupervisor(model_provider="mock")
        p = SystemTaskPayload(task_id="TASK-STORE", target_identifier="T", primary_metric=10.0)
        dossier = sup.process_task(p)
        assert dossier.dossier_id in sup.dossier_registry

    def test_supervisor_audit_hash_present(self):
        """Processed dossier should have audit hash."""
        sup = SystemSupervisor(model_provider="mock")
        p = SystemTaskPayload(task_id="TASK-AUDIT", target_identifier="T", primary_metric=10.0)
        dossier = sup.process_task(p)
        assert dossier.audit_hash
        assert len(dossier.audit_hash) == 64  # SHA-256 hex length


# ==============================================================================
# API ENDPOINT TESTS
# ==============================================================================

class TestAPI:
    def test_health_endpoint(self):
        """Health endpoint should return healthy status."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "HEALTHY"

    def test_audit_endpoint(self):
        """Audit endpoint should process valid payload."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.post("/api/audit", json={
            "task_id": "API-TEST-001",
            "target_identifier": "TARGET-API",
            "primary_metric": 35.0,
            "secondary_metric": 8.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["overall_urgency"] == "ELEVATED_RISK"

    def test_audit_endpoint_rejects_invalid(self):
        """Audit endpoint should reject invalid payloads."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.post("/api/audit", json={
            "task_id": "",  # empty - invalid
            "target_identifier": "T",
            "primary_metric": 10.0,
        })
        assert resp.status_code == 422  # Validation error

    def test_chat_endpoint(self):
        """Chat endpoint should return a response."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.post("/api/chat", json={"query": "system status"})
        assert resp.status_code == 200
        assert "response" in resp.json()

    def test_metrics_endpoint(self):
        """Metrics endpoint should return operational data."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "system_status" in data
