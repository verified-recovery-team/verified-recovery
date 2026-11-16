# Verified Recovery

**A deterministic, policy-guided resilience orchestrator for distributed applications.**

Damascus University — Computer and Automation Engineering
Academic Year: 2026–2027

## 1. Overview

Verified Recovery is a graduation project that aims to improve the resilience of distributed applications through monitoring, diagnosis, policy-guided recovery, and verification.

The project uses Kubernetes to manage a distributed microservices application and introduces an external orchestrator that interacts with the cluster and its monitoring infrastructure.

The current implementation provides:

- Kubernetes workload inspection.
- Prometheus CPU metrics retrieval.
- Deployment restart and scaling through a REST API.
- Persistent incident recording and retrieval.
- Infrastructure monitoring through Grafana.

Automated failure detection, diagnosis, and recovery orchestration are planned for subsequent development stages.

## 2. Architecture

The current environment consists of:

1. **Online Boutique:** A 12-service microservices application deployed on Kubernetes.
2. **Kubernetes:** Manages application workloads and deployment replicas.
3. **Prometheus:** Collects and stores infrastructure metrics.
4. **Grafana:** Visualizes monitoring data.
5. **FastAPI Orchestrator:** Provides REST interfaces for monitoring and Kubernetes operations.
6. **SQLite:** Stores incident records.

The intended recovery workflow is:

`Detection → Diagnosis → Policy → Action → Verification → Fallback`

The complete automated workflow is a project objective, not a currently completed feature.

## 3. Technologies

| Technology | Role |
|---|---|
| Python | Orchestrator implementation |
| FastAPI | REST API |
| Kubernetes | Container orchestration and deployment management |
| Minikube | Local Kubernetes environment |
| Docker | Container runtime |
| Prometheus | Metrics collection and querying |
| Grafana | Monitoring dashboards |
| Helm | Monitoring stack deployment |
| SQLite | Incident persistence |
| HTTPX | HTTP communication with Prometheus |
| Pydantic Settings | Configuration management |
| Pytest | Automated testing |
| Git/GitHub | Version control and collaboration |

## 4. Implemented API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check orchestrator health |
| GET | `/pods` | Retrieve pod information |
| GET | `/cpu` | Retrieve CPU metrics from Prometheus |
| POST | `/deployments/{namespace}/{name}/restart` | Restart a deployment |
| PATCH | `/deployments/{namespace}/{name}/scale` | Change deployment replica count |
| POST | `/incidents` | Create an incident record |
| GET | `/incidents` | List incident records |
| GET | `/incidents/{incident_id}` | Retrieve an incident |

Interactive API documentation is available at `/docs` when the orchestrator is running.

## 5. Repository Structure

```text
verified-recovery/
├── deploy/                 # Online Boutique deployment
├── docs/                   # Project documentation and evidence
├── load/                   # Load testing work
├── orchestrator/
│   ├── app/
│   │   ├── api/routes/     # REST endpoints
│   │   ├── integrations/   # Kubernetes, Prometheus, SQLite
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/unit/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── telemetry/              # Prometheus and Grafana configuration
├── README.md
└── .gitignore
```

## 6. Running the Project

### Prerequisites

- Docker
- kubectl
- Minikube
- Helm
- Python 3
- Git

### Start Kubernetes

```bash
minikube start --driver=docker --cpus=4 --memory=8192
kubectl get nodes
```

### Deploy Online Boutique

```bash
kubectl apply -f deploy/online-boutique.yaml
kubectl get pods
```

Wait until the application pods are running.

### Configure the orchestrator

Create a root `.env` file:

```env
PROMETHEUS_URL=http://127.0.0.1:9090
```

Create and activate the Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r orchestrator/requirements-dev.txt
```

### Start Prometheus and Grafana

Deploy the monitoring stack using the Helm configuration in `telemetry/values.yaml`, then apply the custom recording rules:

```bash
kubectl apply -f telemetry/custom-rules.yaml
```

Forward the Prometheus service:

```bash
kubectl port-forward -n monitoring \
  svc/kps-kube-prometheus-stack-prometheus 9090:9090
```

Keep this terminal running.

### Start the orchestrator

From the repository root:

```bash
.venv/bin/uvicorn orchestrator.app.main:app \
  --host 127.0.0.1 --port 8000
```

Open:

`http://127.0.0.1:8000/docs`

### Run tests

From the repository root:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q
```

Latest verified result: **22 passed, 9 skipped.**

## 7. Demonstrated Capabilities

The following capabilities have been tested:

- Deployment of all 12 Online Boutique services.
- Functional product browsing, cart operations, and checkout.
- Prometheus metrics retrieval through the orchestrator.
- Pod inspection through the orchestrator.
- Deployment restart and scaling operations.
- Persistent incident creation and retrieval.
- Scaling cartservice to zero replicas through the API.
- Restoring cartservice to one replica through the API.
- Successful Kubernetes rollout and frontend cart verification after restoration.

The cartservice experiment demonstrates direct control of a real Kubernetes workload through the orchestrator API.

## 8. Development Status

### Implemented

- Kubernetes environment and Online Boutique deployment.
- Prometheus and Grafana monitoring foundation.
- FastAPI orchestrator.
- Kubernetes integration.
- Prometheus CPU metrics integration.
- Deployment restart and scaling endpoints.
- SQLite incident storage and API.
- Unit testing and live integration verification.

### Remaining project work

- OpenTelemetry distributed tracing.
- Additional fault injection and telemetry experiments.
- Controlled load generation and baseline measurements.
- Automated failure detection.
- Application-level diagnosis.
- Deterministic recovery policies.
- Automated recovery and post-action verification.
- Fallback handling.

## 9. Documentation

- `docs/devlog.md` — Development history.
- `docs/technical-documentation.md` — Detailed technical documentation.
- `docs/claude-handover.md` — Development handover context.
- `docs/professor-presentation.md` — Demonstration scenario and presentation summary.

---

**Project:** Verified Recovery
**Institution:** Damascus University
**Academic Year:** 2026–2027