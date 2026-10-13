"""
FastAPI REST API Server for Hypertensive Crisis Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Hypertensive Crisis Agent API",
    description="Enterprise Distributed Component Platform (Cardiology & Intensive Care Systems)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
def security_exception_handler(request, exc: SecurityException):
    return JSONResponse(status_code=422, content={"detail": "Potential identifying information is not accepted."})


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "hypertensive-crisis-agent", "domain": "Cardiology & Intensive Care Systems", "standard": "Experimental generic audit; not a clinical guideline implementation", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "RUNNING"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        if isinstance(e, SecurityException):
            raise HTTPException(status_code=422, detail="Potential identifying information is not accepted.") from None
        raise


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
