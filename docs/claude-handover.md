# Verified Recovery — Project Handover for Claude

## 1. Project identity

**Project:** Verified Recovery  
**Description:** A deterministic, policy-guided resilience orchestrator for distributed applications.  
**University:** Damascus University  
**Department:** Computer and Automation Engineering  
**Academic year:** 2026–2027  
**Repository:** `/home/khaled/verified-recovery`  
**Branch:** `main`

The project uses Google Online Boutique, a 12-microservice application, as its reference distributed system.

The long-term objective is to build a system that can:

1. Detect service or infrastructure problems.
2. Diagnose the likely cause using telemetry.
3. Select an allowed recovery action according to deterministic policies.
4. Execute the action.
5. Verify whether the system recovered.
6. Record the result and use a fallback when necessary.

**Important:** The current implementation is the foundation for this workflow. The complete automated detection, diagnosis, policy selection, recovery, and verification pipeline has NOT been implemented yet.

---

## 2. Working principles and instructions

Follow these instructions when helping with this project:

- Be concise and explain the purpose of each task.
- The user is currently under time pressure. Provide ready-to-use content when requested, with a short explanation of its purpose.
- Do not assume a command succeeded. Wait for actual terminal output before confirming results.
- Do not claim that tests, deployments, or integrations work without evidence.
- Do not provide large code dumps unless requested. When implementation coaching is requested, explain the objective and expected behavior first.
- Keep work organized into explicit milestones.
- Do not commit or push changes unless the user explicitly approves.
- Preserve the project's architecture and academic objectives.
- Do not begin Phase 2 while Phase 1 still has outstanding team deliverables.
- Distinguish clearly between implemented, tested, demonstrated, planned, and incomplete features.

---

## 3. Current project status

The user's individual Phase 1 orchestrator work has been implemented, tested, demonstrated, and pushed.

The repository was last confirmed clean and synchronized with `origin/main`:

```text
## main...origin/main
```

Relevant commits include:

- `233ff6d Add SQLite incident logging and API`
- `3c02170 Add Kubernetes deployment recovery actions`
- `5b90566 Add Prometheus CPU metrics integration`
- `1c4f478 refactor: organize orchestrator into modular components`
- `f161cbb Add FastAPI skeleton with health and pods routes`
- `d59b742 chore: update README`
- `e406dcf Add sum_rate5m recording rule for dashboard CPU panels`
- `960ba12 Add devlog entry 1: environment and Online Boutique deployment`

Do not assume the repository is still clean without checking `git status`.

### Completed individual work

- Deployed Online Boutique to Minikube.
- Deployed Prometheus and Grafana using Helm.
- Configured custom Prometheus recording rules.
- Built a modular FastAPI orchestrator.
- Implemented Kubernetes pod and deployment integrations.
- Implemented Prometheus CPU metrics integration.
- Implemented deployment restart and scaling APIs.
- Implemented SQLite-based incident storage and API.
- Added unit tests for the integrations and incident store.
- Tested the API against the live Kubernetes cluster.
- Demonstrated scaling a service down to zero replicas and restoring it.
- Verified that the Online Boutique application worked after restoration.

The user's individual orchestrator contribution is complete for the current Phase 1 scope.

**Overall Phase 1 is not yet complete:** teammate deliverables and final integration/evidence remain outstanding.

---

## 4. Environment

The development environment:

| Component | Version / Configuration |
|---|---|
| Host OS | Arch Linux |
| RAM | 16 GB DDR5 |
| Docker | 29.9.1 |
| Minikube | v1.38.1 |
| Helm | v4.3.0 |
| Kubernetes | v1.35.1 |
| Minikube driver | Docker |
| Minikube CPUs | 4 |
| Minikube memory | 8192 MB |
| Cluster nodes | One node: `minikube` |

Online Boutique was deployed from manifest `deploy/online-boutique.yaml`, using version `v0.10.7`.

The application consists of 12 microservices.

Prometheus and Grafana are deployed in the `monitoring` namespace through the Helm release `kps`.

---

## 5. Repository structure

The relevant project structure:

```text
verified-recovery/
├── .env
├── .gitignore
├── README.md
├── data/
│   └── incidents.db
├── deploy/
│   └── online-boutique.yaml
├── docs/
│   ├── devlog.md
│   ├── technical-documentation.md
│   ├── claude-handover.md
│   └── img/
│       ├── pods-running.png
│       └── shop-home.png
├── load/
├── orchestrator/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── cpu.py
│   │   │       ├── deployments.py
│   │   │       ├── health.py
│   │   │       ├── incidents.py
│   │   │       └── pods.py
│   │   ├── integrations/
│   │   │   ├── incident_store.py
│   │   │   ├── kubernetes.py
│   │   │   └── prometheus.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   └── unit/
│   │       ├── test_incident_store.py
│   │       ├── test_kubernetes_integration.py
│   │       └── test_prometheus_integration.py
│   ├── requirements.txt
│   └── requirements-dev.txt
└── telemetry/
    ├── values.yaml
    └── custom-rules.yaml
```

Notes:

- `.env` is local configuration and must not be committed.
- `data/incidents.db` is local runtime data and must not be committed.
- The virtual environment, Python caches, and pytest cache are local development artifacts.
- Do not expose secrets or local environment values in documentation.

---

## 6. Implemented architecture

The orchestrator is a FastAPI application with separate API routes and integration modules.

### Application startup

`orchestrator/app/main.py` uses an application lifespan handler to initialize:

- `PrometheusIntegration`
- `KubernetesIntegration`
- `IncidentStore`

These integrations are made available to the API through application state.

Configuration is managed in `orchestrator/app/config.py` using Pydantic Settings and the local `.env` file.

### Kubernetes integration

`orchestrator/app/integrations/kubernetes.py` uses the Kubernetes Python client:

- `CoreV1Api` for pod information.
- `AppsV1Api` for deployment operations.

It supports dependency injection so that tests can use mocked Kubernetes API clients.

### Prometheus integration

`orchestrator/app/integrations/prometheus.py` uses HTTPX to query the Prometheus HTTP API.

It retrieves CPU usage using the custom five-minute recording rule and returns pod-level information, including namespace, pod, node, and CPU usage.

### Incident storage

`orchestrator/app/integrations/incident_store.py` uses Python's standard-library SQLite support.

The incident table stores:

- ID
- Creation timestamp
- Namespace
- Resource type
- Resource name
- Trigger
- Diagnosis
- Action
- Status
- Additional details as JSON

The store supports creation, retrieval, and paginated listing.

**Limitation:** Incident records are currently created manually through the API. They are not automatically generated from Prometheus alerts or Kubernetes events, and are not automatically linked to recovery actions.

---

## 7. Implemented API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/pods` | List pods and their status |
| GET | `/cpu` | Retrieve CPU metrics from Prometheus |
| POST | `/deployments/{namespace}/{name}/restart` | Trigger a deployment rollout restart |
| PATCH | `/deployments/{namespace}/{name}/scale` | Change desired deployment replicas |
| POST | `/incidents` | Create an incident record |
| GET | `/incidents` | List incidents with pagination |
| GET | `/incidents/{incident_id}` | Retrieve a specific incident |

FastAPI also provides interactive API documentation at `/docs`.

### Important distinction

The restart and scaling endpoints execute explicit operations requested through the API. They do not independently detect problems or decide when to recover a service.

---

## 8. Monitoring implementation

Prometheus and Grafana provide infrastructure monitoring.

Custom recording rules are defined in `telemetry/custom-rules.yaml`, including:

- CPU usage using an instantaneous rate.
- CPU usage using a five-minute rate.
- Container memory working set.

The rules aggregate relevant metrics by namespace, pod, and node.

Grafana dashboards provide visibility into CPU usage, memory usage, and container restarts.

Prometheus can be accessed locally through:

```bash
kubectl port-forward -n monitoring \
  svc/kps-kube-prometheus-stack-prometheus 9090:9090
```

The local `.env` configuration uses the variable:

```text
PROMETHEUS_URL
```

Do not include private configuration values in public documentation.

**OpenTelemetry tracing is not yet complete.** Do not claim distributed tracing coverage has been implemented.

---

## 9. Testing and verification evidence

### Unit tests

The verified test command:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q
```

Recorded output:

```text
22 passed, 9 skipped in 2.17s
```

Report the result exactly. Nine tests were skipped; do not describe them as passed.

### Live API verification

The following behavior was tested against the running cluster:

- `/health` returned HTTP 200.
- `/pods` returned Kubernetes pod information.
- `/cpu` returned metrics for the `default` and `monitoring` namespaces.
- Deployment restart was tested against `frontend`.
- Deployment scaling was tested against `frontend`.
- Incident creation returned HTTP 201.
- Incident listing and retrieval returned successful responses.
- Retrieving a nonexistent incident returned HTTP 404.
- Incident data remained available after restarting the API process.

### Cartservice recovery demonstration

A live acceptance scenario was performed:

1. `cartservice` initially had one ready replica.
2. The orchestrator API was used to scale it to zero.
3. Kubernetes showed zero deployment replicas and no cartservice pods.
4. The orchestrator API was used to restore the replica count to one.
5. Kubernetes successfully completed the rollout.
6. The new cartservice pod reached `Running` and `Ready`.
7. The Online Boutique frontend was accessed through a local port-forward.
8. The user confirmed that the shop worked and that adding a product to the cart worked.

This is an important demonstration of the orchestrator's ability to perform controlled Kubernetes operations through its API and verify the result using Kubernetes state and application behavior.

Do not describe this as automatic failure detection or automatic recovery. The scale operation was explicitly requested through the API.

---

## 10. Technology choices and rationale

| Technology | Role | Why it was used |
|---|---|---|
| Python | Main implementation language | Suitable ecosystem for APIs, automation, and infrastructure integrations |
| FastAPI | Orchestrator API | Provides structured REST endpoints, validation, and automatic API documentation |
| Kubernetes | Container orchestration | Runs and manages the distributed application |
| Minikube | Local Kubernetes cluster | Enables development and testing without a remote cluster |
| Docker | Container runtime | Runs the local cluster and application containers |
| Online Boutique | Reference microservices application | Provides a realistic distributed system for experiments |
| Prometheus | Metrics collection and querying | Provides quantitative telemetry for monitoring and future diagnosis |
| Grafana | Monitoring dashboards | Makes system behavior and metrics easier to inspect |
| Helm | Kubernetes package management | Simplifies deployment and configuration of the monitoring stack |
| Kubernetes Python client | Kubernetes API integration | Allows the orchestrator to inspect pods and modify deployments programmatically |
| HTTPX | HTTP client | Communicates with the Prometheus API |
| SQLite | Incident persistence | Provides simple local persistent storage without requiring a separate database server |
| Pydantic Settings | Configuration | Centralizes application configuration and environment-variable handling |
| Pytest | Automated testing | Verifies integrations and application behavior |
| Git and GitHub | Version control and collaboration | Tracks changes, supports collaboration, and preserves project milestones |

---

## 11. Remaining Phase 1 work

The following work belongs to the team and must be completed before declaring Phase 1 finished.

### Musab

- Complete the Chaos Mesh fault-injection smoke test.
- Demonstrate killing a cartservice pod and observing the resulting behavior.
- Complete service-level latency and error-rate metrics for at least:
  - frontend
  - checkoutservice
- Provide test evidence and relevant screenshots.

### Mohammed

- Complete Locust load generation.
- Run the agreed baseline experiments.
- Produce a baseline table containing:
  - p50 latency
  - p95 latency
  - p99 latency
  - requests per second
  - error rate
- Provide evidence for two runs.

### Team integration and documentation

- Integrate and review teammate contributions.
- Ensure the required Phase 1 evidence is available.
- Confirm all required work is merged into the main branch.
- Prepare a reproducible demonstration.

OpenTelemetry tracing coverage is also still required/planned; at minimum, the target coverage should include frontend and checkoutservice. Do not claim it is complete until evidence confirms it.

---

## 12. Phase 1 demonstration scenario

The intended team demonstration should show:

1. Minikube running.
2. All 12 Online Boutique services healthy.
3. The shop working through the browser.
4. Prometheus and Grafana displaying monitoring data.
5. Locust generating traffic and producing baseline measurements.
6. Chaos Mesh injecting a controlled failure.
7. The orchestrator API scaling cartservice to zero.
8. The resulting application behavior.
9. The orchestrator API restoring cartservice to one replica.
10. Kubernetes confirming the new pod is ready.
11. The shop working again.
12. The team presenting its test results and evidence.

The exact order may be adjusted to match what is actually available and verified on demonstration day.

---

## 13. Important academic and technical limitations

Never claim the following features are already implemented:

- Automatic incident detection.
- Automatic diagnosis.
- AI-based diagnosis.
- Deterministic policy selection and enforcement.
- Automatic recovery decisions.
- Automatic recovery execution based on detected incidents.
- Post-recovery verification as an automated orchestrator workflow.
- Automatic fallback.
- Complete OpenTelemetry tracing.
- A fully autonomous self-healing system.

These are part of the broader project direction or future implementation work.

The current system is a working foundation: it deploys and monitors a distributed application, exposes operational interfaces, executes explicit Kubernetes actions, and stores incident records.

The distinction matters academically. The project should demonstrate real engineering progress without overstating its current capabilities.

---

## 14. Next tasks for Claude

When continuing this project:

1. Read `README.md` and `docs/technical-documentation.md`.
2. Read this handover before proposing changes.
3. Check the actual repository state and current branch.
4. Verify documentation against the implementation where necessary.
5. Help prepare the professor-facing explanation and demonstration scenario.
6. Help identify and track the remaining Phase 1 team deliverables.
7. Do not begin Phase 2 implementation until Phase 1 is formally closed or the user explicitly changes the plan.

The immediate priority is documentation, professor presentation preparation, and Phase 1 coordination—not adding new features.

**Final rule:** Be precise about what exists, what has been tested, what has been demonstrated, and what remains planned.