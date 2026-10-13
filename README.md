# Hypertensive Crisis Agent

An **educational** browser blood-pressure screen and preserved experimental Python audit workflows. **Not a clinically validated decision-support or treatment device.**

## Browser application

Open `web/index.html` directly in a modern browser. Enter systolic/diastolic blood pressure, indicate possible acute symptoms or organ injury, and identify pregnancy/postpartum context. The page runs locally without Python, network requests, analytics, or input storage. Do not enter identifiable patient information.

The screening rule uses the 2025 AHA/ACC severe BP threshold (**SBP >180 or DBP >120 mm Hg**) and explains that suspected acute target-organ damage requires emergency evaluation. It does not diagnose organ injury, prescribe drugs, or set condition-specific treatment targets. Unknown findings remain indeterminate. Pregnancy/postpartum and other condition-specific emergencies require separate clinical pathways. Emergency symptoms require emergency care regardless of the screening result.

Clinical references:
- [2025 AHA/ACC high blood pressure guideline, §6.2](https://www.jacc.org/doi/10.1016/j.jacc.2025.05.007)
- [2024 AHA acute-care BP statement](https://professional.heart.org/en/science-news/management-of-elevated-blood-pressure-in-the-acute-care-setting)
- [2024 ESC hypertension guideline](https://academic.oup.com/eurheartj/article/45/38/3912/7741010)

## Legacy Python interfaces

The existing interfaces remain for backward compatibility, but their generic primary/secondary metric thresholds are **not** validated clinical hypertensive-crisis algorithms:

- `python cli.py` — generic supervisor, batch CSV, HMAC audit chain and FastAPI application (`agents/`)
- `python htn_crisis.py` — legacy standalone generic-metric evaluator
- `python -m hypertensive_crisis_agent.cli` — separate package implementation

No external LLM provider is implemented. The deterministic mock is for testing only.

### Install, test, and use

Python 3.10+ is supported. Node.js 22 is used only to test the browser logic.

```bash
python -m pip install -e ".[api,test]"
python -m pytest -q
node --test web/app.test.cjs
python cli.py audit --task-id DEMO-001 --target SYNTH-001 --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The experimental FastAPI server exposes `/health`, `/api/audit`, `/api/chat`, `/metrics` and `/api/audit/logs`. It does **not** power the browser page.

### Docker

```bash
docker build -t hypertensive-crisis-agent .
docker run --rm -p 127.0.0.1:8000:8000 -e AUDIT_SECRET_KEY="<strong-local-key>" hypertensive-crisis-agent
```

For Compose, supply a strong `AUDIT_SECRET_KEY` in the host environment; never commit it.

## Security and deployment

The Python regex identifier filter is **not** guaranteed de-identification or HIPAA compliance. Its HMAC-SHA256 chain is in-memory and is not a durable clinical audit log. Do not process real patient identifiers or use output for clinical decisions.

The browser requires only HTML/CSS/JavaScript, not Pyodide. CI runs Python and JavaScript tests and attempts to publish the static `web/` directory on `master` using GitHub Pages. A public link should be used only after successful Pages configuration and live verification. Supported browsers: modern Chrome, Firefox, Safari, and Edge (functional browser testing remains necessary).

## License

[MIT](LICENSE).
