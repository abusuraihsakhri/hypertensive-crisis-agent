# Hypertensive Crisis Agent

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Hypertensive Crisis Agent** is an advanced analytical and computational platform implementing Emergency vs Urgency End-Organ Damage & MAP Reduction Titrator.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`EndOrganDamageScannerAgent`**: Specialized Sub-Agent 1 for hypertensive-crisis-agent
- **`MAPReductionTargetAgent`**: Specialized Sub-Agent 2 for hypertensive-crisis-agent
- **`IVAntihypertensiveAdvisorAgent`**: Specialized Sub-Agent 3 for hypertensive-crisis-agent

---

## 💻 CLI Quickstart & Usage

### 1. Run a Single Audit
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Query the Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task/case identifier | `TASK-2026-001` |
| `--target` | Target entity or specimen identifier | `KEY-TARGET-01` |
| `--primary` | Primary metric measurement (0-1000) | `28.5` |
| `--secondary` | Secondary metric measurement (0-1000) | `14.2` |
| `--critical` | Flag as critical/STAT emergency | `False` |
| `--status` | Status descriptor (e.g., NOMINAL, DISCORDANT) | `DISCORDANT` |

### Input Data Schema (Batch CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value (0-1000) | Required |
| `secondary_metric` | Secondary measurement value (0-1000) | Optional |
| `is_critical_flag` | Critical escalation flag (true/false) | Optional |
| `status_descriptor` | Status code (NOMINAL, DISCORDANT, etc.) | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers from outbound data.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with integrity verification for every evaluation and state transition.
* **Input Validation:** Pydantic models with bounds checking (metrics 0-1000), string length limits, and control character sanitization.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables
| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit trail signing | Ephemeral (random per session) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## 🧪 Testing & Verification

Install dev dependencies:

```bash
pip install pytest httpx
```

Run the automated test suite:

```bash
pytest -v
```

Test categories:
- **Unit tests** (`test_htn_crisis.py`) — Core sub-agents, coordinator, CLI, domain registry
- **Security & API tests** (`test_security_and_api.py`) — PHI guard, audit trail, input validation, FastAPI endpoints
- **Module tests** (`tests/test_hypertensive_crisis_agent.py`) — Workers, supervisor consensus, CLI integration
- **Enrichment tests** (`tests/test_enrichment.py`) — Enrichment suite engines and threshold escalation

Execute high-throughput simulation benchmark:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t hypertensive-crisis-agent .
docker run -p 8000:8000 hypertensive-crisis-agent
```
